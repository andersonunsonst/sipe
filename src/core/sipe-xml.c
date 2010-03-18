/**
 * @file sipe-xml.c
 *
 * pidgin-sipe
 *
 * Copyright (C) 2010 SIPE Project <http://sipe.sourceforge.net/>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

/*
 * This code is loosely based on libpurple xmlnode.c
 */

#include <stdarg.h>

#include "libxml/parser.h"
#include "glib.h"

#include "sipe-xml.h"
#include "sipe.h"       /* TEMPORARY: to include sipe-utils.h without errors */
#include "sipe-utils.h"
#include "sipe-backend-debug.h"

struct _sipe_xml {
	gchar *name;
	sipe_xml *parent;
	sipe_xml *sibling;
	sipe_xml *first;
	sipe_xml *last;
	GString *data;
	GHashTable *attributes;
};

struct _parser_data {
	sipe_xml *root;
	sipe_xml *current;
	gboolean error;
};

static void callback_start_element(void *user_data, const xmlChar *name, const xmlChar **attrs)
{
	struct _parser_data *pd = user_data;
	sipe_xml *node;

	if (!name || pd->error) return;

	node = g_new0(sipe_xml, 1);
	node->name = g_strdup((gchar *)name);

	if (!pd->root) {
		pd->root = node;
	} else {
		sipe_xml *current = pd->current;

		node->parent = current;
		if (current->last) {
			current->last->sibling = node;
		} else {
			current->first = node;
		}
		current->last = node;
	}

	if (attrs) {
		const xmlChar *key;

		node->attributes = g_hash_table_new_full(g_str_hash,
							 (GEqualFunc) sipe_strcase_equal,
							 g_free, g_free);
		while ((key = *attrs++) != NULL) {
			g_hash_table_insert(node->attributes,
					    g_strdup((gchar *) key),
					    g_strdup((gchar *) *attrs++));
		}
	}

	pd->current = node;
}

static void callback_end_element(void *user_data, const xmlChar *name)
{
	struct _parser_data *pd = user_data;

	if (!name || !pd->current || pd->error) return;

	if (pd->current->parent)
		pd->current = pd->current->parent;
}

static void callback_characters(void *user_data, const xmlChar *text, int text_len)
{
	struct _parser_data *pd = user_data;
	sipe_xml *node;

	if (!pd->current || pd->error || !text || !text_len) return;

	node = pd->current;
	if (node->data)
		node->data = g_string_append_len(node->data, (gchar *)text, text_len);
	else
		node->data = g_string_new_len((gchar *)text, text_len);
}

static void callback_error(void *user_data, const char *msg, ...)
{
	struct _parser_data *pd = user_data;
	gchar *errmsg;
	va_list args;

	pd->error = TRUE;

	va_start(args, msg);
	errmsg = g_strdup_vprintf(msg, args);
	va_end(args);

	SIPE_DEBUG_ERROR("error parsing xml string: %s", errmsg);
	g_free(errmsg);
}

static void callback_serror(void *user_data, xmlErrorPtr error)
{
	struct _parser_data *pd = user_data;

	if (error && (error->level == XML_ERR_ERROR ||
	              error->level == XML_ERR_FATAL)) {
		pd->error = TRUE;
		SIPE_DEBUG_ERROR("XML parser error: Domain %i, code %i, level %i: %s",
				 error->domain, error->code, error->level,
				 error->message ? error->message : "(null)");
	} else if (error) {
		SIPE_DEBUG_WARNING("XML parser error: Domain %i, code %i, level %i: %s",
		                   error->domain, error->code, error->level,
				   error->message ? error->message : "(null)");
	} else {
		/* *sigh* macro expects at least two parameters */
		SIPE_DEBUG_WARNING("XML parser error%s", "");
	}
}

/* API doesn't accept const data structure */
static xmlSAXHandler parser = {
	NULL,                   /* internalSubset */
	NULL,                   /* isStandalone */
	NULL,                   /* hasInternalSubset */
	NULL,                   /* hasExternalSubset */
	NULL,                   /* resolveEntity */
	NULL,                   /* getEntity */
	NULL,                   /* entityDecl */
	NULL,                   /* notationDecl */
	NULL,                   /* attributeDecl */
	NULL,                   /* elementDecl */
	NULL,                   /* unparsedEntityDecl */
	NULL,                   /* setDocumentLocator */
	NULL,                   /* startDocument */
	NULL,                   /* endDocument */
	callback_start_element, /* startElement */
	callback_end_element,   /* endElement   */
	NULL,                   /* reference */
	callback_characters,    /* characters */
	NULL,                   /* ignorableWhitespace */
	NULL,                   /* processingInstruction */
	NULL,                   /* comment */
	NULL,                   /* warning */
	callback_error,         /* error */
	NULL,                   /* fatalError */
	NULL,                   /* getParameterEntity */
	NULL,                   /* cdataBlock */
	NULL,                   /* externalSubset */
	XML_SAX2_MAGIC,         /* initialized */
	NULL,                   /* _private */
	NULL,                   /* startElementNs */
	NULL,                   /* endElementNs   */
	callback_serror,        /* serror */
};

sipe_xml *sipe_xml_parse(const gchar *string, gsize length)
{
	sipe_xml *result = NULL;

	if (string && length) {
		struct _parser_data *pd = g_new0(struct _parser_data, 1);

		if (xmlSAXUserParseMemory(&parser, pd, string, length))
			pd->error = TRUE;

		if (pd->error) {
			sipe_xml_free(pd->root);
		} else {
			result = pd->root;
		}

		g_free(pd);
	}

	return result;
}

void sipe_xml_free(sipe_xml *node)
{
	sipe_xml *child;

	if (!node) return;

	/* we don't support partial tree deletion */
	if (node->parent != NULL) {
		SIPE_DEBUG_ERROR("sipe_xml_free: partial delete attempt! Expect crash or memory leaks...%s", "");
	}

	/* free children */
	child = node->first;
	while (child) {
		sipe_xml *tmp = child->sibling;
		child->parent = NULL; /* detach from tree, see above */
		sipe_xml_free(child);
		child = tmp;
	}

	/* free node */
	g_free(node->name);
	if (node->data)       g_string_free(node->data, TRUE);
	if (node->attributes) g_hash_table_destroy(node->attributes);
	g_free(node);
}

gchar *sipe_xml_to_string(const sipe_xml *node)
{
	/* @TODO: implement me :-) */
	(void) node;
	return NULL;
}

sipe_xml *sipe_xml_get_child(const sipe_xml *parent, const gchar *name)
{
	gchar **names;
	sipe_xml *child = NULL;

	if (!parent || !name) return NULL;

	/* 0: child name */
	/* 1: trailing path (optional) */
	names = g_strsplit(name, "/", 2);

	for (child = parent->first; child; child = child->sibling) {
		if (sipe_strequal(names[0], child->name))
			break;
	}

	/* recurse into path */
	if (child && names[1])
		child = sipe_xml_get_child(child, names[1]);

	g_strfreev(names);
	return child;
}

sipe_xml *sipe_xml_get_next_twin(const sipe_xml *node)
{
	sipe_xml *sibling;

	if (!node) return NULL;

	for (sibling = node->sibling; sibling; sibling = sibling->sibling) {
		if (sipe_strequal(node->name, sibling->name))
			return sibling;
	}		
	return NULL;
}

const gchar *sipe_xml_get_attribute(const sipe_xml *node, const gchar *attr)
{
	if (!node || !attr || !node->attributes) return NULL;
	return(g_hash_table_lookup(node->attributes, attr));
}

gint sipe_xml_get_int_attribute(const sipe_xml *node, const gchar *attr,
				gint fallback)
{
	const gchar *value = sipe_xml_get_attribute(node, attr);
	return(value ? atoi(value) : fallback);
}

gchar *sipe_xml_get_data(const sipe_xml *node)
{
	if (!node || !node->data || !node->data->str) return NULL;
	return g_strdup(node->data->str);
}

/*
  Local Variables:
  mode: c
  c-file-style: "bsd"
  indent-tabs-mode: t
  tab-width: 8
  End:
*/
