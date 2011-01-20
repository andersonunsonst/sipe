/**
 * @file sipe-user.c
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

#include <glib.h>

#include "sipe-common.h"
#include "sipmsg.h"
#include "sip-transport.h"
#include "sipe-backend.h"
#include "sipe-core.h"
#include "sipe-core-private.h"
#include "sipe-dialog.h"
#include "sipe-session.h"
#include "sipe-utils.h"

static gboolean process_info_typing_response(struct sipe_core_private *sipe_private,
					     struct sipmsg *msg,
					     SIPE_UNUSED_PARAMETER struct transaction *trans)
{
	/* Indicates dangling IM session which needs to be dropped */
	if (msg->response == 408 || /* Request timeout */
	    msg->response == 480 || /* Temporarily Unavailable */
	    msg->response == 481) { /* Call/Transaction Does Not Exist */
		gchar *with = parse_from(sipmsg_find_header(msg, "To"));
		struct sip_session *session = sipe_session_find_im(sipe_private, with);
		struct sip_dialog *dialog = sipe_dialog_find(session, with);
		if (dialog) {
			SIPE_DEBUG_INFO_NOFORMAT("process_info_typing_response: assuming dangling IM session, dropping it.");
			sip_transport_bye(sipe_private, dialog);

			/* We might not get a valid reply to our BYE,
			   so make sure the dialog is removed for sure. */
			sipe_dialog_remove(session, with);
		}
		g_free(with);
	}	
	return(TRUE);
}

void sipe_core_user_feedback_typing(struct sipe_core_public *sipe_public,
				    const gchar *to)
{
	struct sipe_core_private *sipe_private = SIPE_CORE_PRIVATE;
	struct sip_session *session = sipe_session_find_im(sipe_private, to);
	struct sip_dialog *dialog = sipe_dialog_find(session, to);

	if (session && dialog && dialog->is_established) {
		sip_transport_info(sipe_private,
				   "Content-Type: application/xml\r\n",
				   "<?xml version=\"1.0\"?>"
				   "<KeyboardActivity>"
				   "<status status=\"type\" />"
				   "</KeyboardActivity>",
				   dialog,
				   process_info_typing_response);
	}
}


/*
  Local Variables:
  mode: c
  c-file-style: "bsd"
  indent-tabs-mode: t
  tab-width: 8
  End:
*/
