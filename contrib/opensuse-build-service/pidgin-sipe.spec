#
# OBS SPEC file to generate a RPM for pidgin-sipe.
#
# It has support for:
#
#     RedHat family (CentOS, Fedora, RHEL)
#     Mandriva
#     SUSE family (openSUSE, SLED, SLES)
#     Windows (mingw32, mingw64)
#

# Build options
%define build_telepathy 0

# Check for mingw32 cross compilation build
#
# Manually add this repository to your private OBS project:
#
#  <repository name="mingw32">
#    <path repository="openSUSE_11.4" project="windows:mingw:win32"/>
#    <arch>i586</arch>
#  </repository>
#
%if "%{_repository}" == "mingw32"
%define purple_sipe_mingw32 1
%define mingw_prefix        mingw32-
%define mingw_cache         %{_mingw32_cache}
%define mingw_configure     %{_mingw32_configure}
%define mingw_datadir       %{_mingw32_datadir}
%define mingw_debug_package %{_mingw32_debug_package}
%define mingw_ldflags       MINGW32_LDFLAGS
%define mingw_libdir        %{_mingw32_libdir}
%define mingw_make          %{_mingw32_make}
%define mingw_makeinstall   %{_mingw32_makeinstall}
%define __strip             %{_mingw32_strip}
%define __objdump           %{_mingw32_objdump}
%define _use_internal_dependency_generator 0
%define __find_requires     %{_mingw32_findrequires}
%define __find_provides     %{_mingw32_findprovides}
%define __os_install_post   %{_mingw32_debug_install_post} \
                            %{_mingw32_install_post}
%endif

# Check for mingw64 cross compilation build
#
# Manually add this repository to your private OBS project:
#
#  <repository name="mingw64">
#    <path repository="openSUSE_11.4" project="windows:mingw:win64"/>
#    <arch>i586</arch>
#  </repository>
#
%if "%{_repository}" == "mingw64"
%define purple_sipe_mingw64 1
%define mingw_prefix        mingw64-
%define mingw_cache         %{_mingw64_cache}
%define mingw_configure     %{_mingw64_configure}
%define mingw_datadir       %{_mingw64_datadir}
%define mingw_debug_package %{_mingw64_debug_package}
%define mingw_ldflags       MINGW64_LDFLAGS
%define mingw_libdir        %{_mingw64_libdir}
%define mingw_make          %{_mingw64_make}
%define mingw_makeinstall   %{_mingw64_makeinstall}
%define __strip             %{_mingw64_strip}
%define __objdump           %{_mingw64_objdump}
%define _use_internal_dependency_generator 0
%define __find_requires     %{_mingw64_findrequires}
%define __find_provides     %{_mingw64_findprovides}
%define __os_install_post   %{_mingw64_debug_install_post} \
                            %{_mingw64_install_post}
%endif

%define purple_plugin    %{?mingw_prefix:%{mingw_prefix}}libpurple-plugin-sipe
%define telepathy_plugin %{?mingw_prefix:%{mingw_prefix}}telepathy-plugin-sipe
%define nsis_package     %{?mingw_prefix:%{mingw_prefix}}pidgin-sipe-nsis


%define purple_develname libpurple-devel

%if 0%{?mdkversion} >= 200910
%ifarch x86_64
%define purple_develname lib64purple-devel
%endif
%if 0%{?mdkversion} >= 201000
%ifnarch x86_64
%define has_libnice 1
%endif
%endif
%endif

%if 0%{?suse_version}
%define nss_develname mozilla-nss-devel
%if 0%{?suse_version} >= 1120
%define has_libnice 1
%if 0%{?suse_version} > 1140
%define has_gstreamer 1
%endif
%endif
%else
%define nss_develname nss-devel
%endif

%if 0%{?suse_version} || 0%{?sles_version}
%define pkg_group Productivity/Networking/Instant Messenger
%endif
%if 0%{?fedora}
%define pkg_group Applications/Internet
%define has_gmime 1
%if 0%{?fedora} >= 11
%define has_libnice 1
%if 0%{?fedora} >= 15
%define has_gstreamer 1
%endif
%endif
%endif
%if 0%{?mdkversion}
%define pkg_group Networking/Instant messaging
%else
%define pkg_group Applications/Internet
%endif

%if 0%{?purple_sipe_mingw32}
Name:           mingw32-pidgin-sipe
%else
%if 0%{?purple_sipe_mingw64}
Name:           mingw64-pidgin-sipe
%else
Name:           pidgin-sipe
%endif
%endif
Summary:        Pidgin protocol plugin to connect to MS Office Communicator
Version:        1.13.3
Release:        1
Source:         pidgin-sipe-%{version}.tar.gz
Group:          %{pkg_group}
License:        GPL-2.0+
URL:            http://sipe.sourceforge.net/

BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%if 0%{?mingw_prefix:1}
#
# Windows cross-compilation build setup
#
BuildArch:      noarch
#!BuildIgnore:   post-build-checks

BuildRequires:  %{mingw_prefix}filesystem >= 23
BuildRequires:  %{mingw_prefix}cross-gcc
BuildRequires:  %{mingw_prefix}cross-binutils
BuildRequires:  %{mingw_prefix}gettext-runtime
BuildRequires:  %{mingw_prefix}cross-pkg-config
BuildRequires:  %{mingw_prefix}glib2-devel >= 2.12.0
BuildRequires:  %{mingw_prefix}libxml2-devel
BuildRequires:  %{mingw_prefix}mozilla-nss-devel
BuildRequires:  %{mingw_prefix}libpurple-devel >= 2.4.0
BuildRequires:  %{mingw_prefix}cross-nsis

# For directory ownership
BuildRequires:  %{mingw_prefix}pidgin

%else
#
# Standard Linux build setup
#
BuildRequires:  %{purple_develname} >= 2.4.0
BuildRequires:  libxml2-devel
BuildRequires:  %{nss_develname}
BuildRequires:  gettext-devel
%if 0%{?has_gmime:1}
BuildRequires:  gmime-devel
%endif
# The following two are required to enable Voice & Video features
%if 0%{?has_libnice:1}
BuildRequires:  libnice-devel
%endif
%if 0%{?has_gstreamer:1}
BuildRequires:  gstreamer-devel
%endif

# Configurable components
%if !0%{?_without_kerberos:1}
BuildRequires:  krb5-devel
%endif

# For directory ownership
BuildRequires:  pidgin
%if %{build_telepathy}
BuildRequires:  pkgconfig(telepathy-glib)
%endif
Requires:       pidgin
%if 0%{?sles_version} == 10
BuildRequires:  gnome-keyring-devel
%endif

# For OBS's "have choice for" for Fedora 11 (only)
%if 0%{?fedora_version} == 11
BuildRequires:  libproxy-mozjs
BuildRequires:  PolicyKit-gnome
%endif

# For OBS's "have choice for" for Mandriva 2010.1 (and up?)
%if 0%{?mdkversion} >= 201010
BuildRequires:  polkit-gnome
%endif

# For OBS's "have choice for" for Mandriva 2011 (and up?)
%if 0%{?mdkversion} >= 201100
BuildRequires:  packagekit-gstreamer-plugin
BuildRequires:  gnome-packagekit-common
%endif

# End Windows cross-compilation/Linux build setup
%endif

Requires:       %{purple_plugin} = %{?epoch:%{epoch}:}%{version}-%{release}
BuildRequires:  libtool
BuildRequires:  intltool
BuildRequires:  glib2-devel >= 2.12.0


%description
A third-party plugin for the Pidgin multi-protocol instant messenger.
It implements the extended version of SIP/SIMPLE used by various products:

    * Microsoft Lync Server 2010
    * Microsoft Office Communications Server (OCS 2007/2007 R2)
    * Microsoft Live Communications Server (LCS 2003/2005)
    * Reuters Messaging

With this plugin you should be able to replace your Microsoft Office
Communicator client with Pidgin.

This package provides the icon set for Pidgin.


%package -n %{purple_plugin}
Summary:        Libpurple protocol plugin to connect to MS Office Communicator
Group:          %{pkg_group}
License:        GPL-2.0+
Obsoletes:      purple-sipe

%description -n %{purple_plugin}
A third-party plugin for the Pidgin multi-protocol instant messenger.
It implements the extended version of SIP/SIMPLE used by various products:

    * Microsoft Lync Server 2010
    * Microsoft Office Communications Server (OCS 2007/2007 R2)
    * Microsoft Live Communications Server (LCS 2003/2005)
    * Reuters Messaging

This package provides the protocol plugin for libpurple clients.


%if %{build_telepathy}
%package -n %{telepathy_plugin}
Summary:        Telepathy connection manager for MS Office Communicator
Group:          %{pkg_group}
License:        GPL-2.0+

%description -n %{telepathy_plugin}
A third-party plugin for the Pidgin multi-protocol instant messenger.
It implements the extended version of SIP/SIMPLE used by various products:

    * Microsoft Lync Server 2010
    * Microsoft Office Communications Server (OCS 2007/2007 R2)
    * Microsoft Live Communications Server (LCS 2003/2005)
    * Reuters Messaging

This package provides the connection manager for the telepathy multi-protocol
instant messaging core.
%endif


%if 0%{?mingw_prefix:1}
%package -n %{nsis_package}
Summary:        Windows Pidgin protocol plugin to connect to MS Office Communicator
Group:          %{pkg_group}
License:        GPL-2.0+

%description -n %{nsis_package}
A third-party plugin for the Pidgin multi-protocol instant messenger.
It implements the extended version of SIP/SIMPLE used by various products:

    * Microsoft Lync Server 2010
    * Microsoft Office Communications Server (OCS 2007/2007 R2)
    * Microsoft Live Communications Server (LCS 2003/2005)
    * Reuters Messaging

This package contains the NSIS installer package of the protocol plugin
for Pidgin on Windows.
%endif


%{mingw_debug_package}


%prep
%setup -q -n pidgin-sipe-%{version}

%build
%if 0%{?mingw_prefix:1}
#
# Windows cross-compilation build
#
%{?env_options}
echo "lt_cv_deplibs_check_method='pass_all'" >>%{mingw_cache}
autoreconf --verbose --install --force
%{mingw_ldflags}="-Wl,--exclude-libs=libintl.a -Wl,--exclude-libs=libiconv.a -lws2_32"
%{mingw_configure} \
        --enable-purple \
%if %{build_telepathy}
        --enable-telepathy
%else
        --disable-telepathy
%endif
%{mingw_make} %{_smp_mflags} || %{mingw_make}

%else
#
# Standard Linux build
#
%if 0%{?sles_version} == 10
export CFLAGS="%optflags -I%{_includedir}/gssapi"
%endif
%if 0%{?mdkversion}
autoreconf --verbose --install --force
%endif
%configure \
	--enable-purple \
%if %{build_telepathy}
        --enable-telepathy
%else
	--disable-telepathy
%endif
make %{_smp_mflags}
make %{_smp_mflags} check

# End Windows cross-compilation/Linux build setup
%endif


%install
%if 0%{?mingw_prefix:1}
#
# Windows cross-compilation install
#
%{mingw_makeinstall}
rm -f %{buildroot}%{mingw_libdir}/purple-2/*.dll.a

# generate NSIS installer package
perl contrib/opensuse-build-service/generate_nsi.pl po/LINGUAS \
	<contrib/opensuse-build-service/pidgin-sipe.nsi.template \
	>%{buildroot}/pidgin-sipe.nsi
( \
	set -e; \
	cd %{buildroot}; \
	makensis \
		-DVERSION=%{version} \
		-DMINGW_LIBDIR=%{buildroot}%{mingw_libdir} \
		-DMINGW_DATADIR=%{buildroot}%{mingw_datadir} \
		pidgin-sipe.nsi \
)
rm -f %{buildroot}/pidgin-sipe.nsi

%else
#
# Standard Linux install
#
%makeinstall

# End Windows cross-compilation/Linux build setup
%endif

find %{buildroot} -type f -name "*.la" -delete -print
# SLES11 defines suse_version = 1110
%if 0%{?suse_version} && 0%{?suse_version} < 1120
rm -r %{buildroot}/%{_datadir}/pixmaps/pidgin/protocols/scalable
%endif
%find_lang pidgin-sipe


%clean
rm -rf %{buildroot}


%files -n %{purple_plugin} -f pidgin-sipe.lang
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README TODO
%if 0%{?mingw_prefix:1}
%{mingw_libdir}/purple-2/libsipe.dll
%else
%{_libdir}/purple-2/libsipe.so
%endif


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING
%if 0%{?mingw_prefix:1}
%{mingw_datadir}/pixmaps/pidgin/protocols/*/sipe.png
%{mingw_datadir}/pixmaps/pidgin/protocols/*/sipe.svg
%else
%{_datadir}/pixmaps/pidgin/protocols/*/sipe.png
# SLES11 defines suse_version = 1110
%if !0%{?suse_version} || 0%{?suse_version} >= 1120
%{_datadir}/pixmaps/pidgin/protocols/*/sipe.svg
%endif
%endif


%if %{build_telepathy}
%files -n %{telepathy_plugin}
%defattr(-, root, root)
%{_libexecdir}/telepathy-sipe
%endif


%if 0%{?mingw_prefix:1}
%files -n %{nsis_package}
%defattr(-, root, root)
/pidgin-sipe-%{version}.exe
%endif


%changelog
* Sun Aug 19 2012 J. D. User <jduser@noreply.com> 1.13.3
- update to 1.13.3

* Sun Jun 10 2012 J. D. User <jduser@noreply.com> 1.13.2
- update to 1.13.2

* Mon Apr 09 2012 J. D. User <jduser@noreply.com> 1.13.1
- update to 1.13.1

* Wed Mar 14 2012 J. D. User <jduser@noreply.com> 1.13.0
- update to 1.13.0

* Mon Dec 12 2011 J. D. User <jduser@noreply.com> 1.12.0-*git*
- we do support Microsoft Lync Server 2010 now.

* Tue Dec 06 2011 J. D. User <jduser@noreply.com> 1.12.0-*git*
- update GPL2 license name

* Sat Nov 12 2011 J. D. User <jduser@noreply.com> 1.12.0-*git*
- add BR gmime-devel for Fedora to have at least one verification platform

* Sun Nov 06 2011 J. D. User <jduser@noreply.com> 1.12.0-*git*
- fix Mandriva 2011 unresolvable BR

* Mon Oct 31 2011 J. D. User <jduser@noreply.com> 1.12.0-*git*
- add BR nss-devel

* Sat Oct 01 2011 J. D. User <jduser@noreply.com> 1.12.0-*git*
- add NSIS package for mingw builds

* Sat Oct 01 2011 J. D. User <jduser@noreply.com> 1.12.0-*git*
- add mingw64 build

* Wed Sep 28 2011 J. D. User <jduser@noreply.com> 1.12.0-*git*
- remove BR mingw32-mozilla-nss-devel, not needed for SSPI.

* Mon Sep 19 2011 J. D. User <jduser@noreply.com> 1.12.0-*git*
- update mingw32 build
- update descriptions

* Mon Aug 29 2011 J. D. User <jduser@noreply.com> 1.12.0
- update to 1.12.0

* Wed Jun 22 2011 J. D. User <jduser@noreply.com> 1.11.2-*git*
- add gstreamer-devel to enable Voice & Video features

* Sat Dec 11 2010 J. D. User <jduser@noreply.com> 1.11.2-*git*
- add optional subpackage for telepathy connection manager

* Tue Nov 02 2010 J. D. User <jduser@noreply.com> 1.11.2
- update to 1.11.2

* Sun Oct 24 2010 J. D. User <jduser@noreply.com> 1.11.1
- update to 1.11.1

* Fri Oct 15 2010 J. D. User <jduser@noreply.com> 1.11.0-*git*
- add mingw32 build configuration

* Sun Oct 03 2010 J. D. User <jduser@noreply.com> 1.11.0
- update to 1.11.0

* Thu Sep 02 2010 J. D. User <jduser@noreply.com> pre-1.11.0-*git*
- Mandriva config for OBS has changed

* Tue May 04 2010 J. D. User <jduser@noreply.com> 1.10.0-*git*
- add libnice build information discovered through OBS testing

* Mon Apr 12 2010 J. D. User <jduser@noreply.com> 1.10.0-*git*
- add NSS build information discovered through OBS testing

* Wed Apr 04 2010 pier11 <pier11@operamail.com> 1.10.0
- release

* Fri Apr 02 2010 J. D. User <jduser@noreply.com> pre-1.10.0-*git*
- Mandriva has too old libtool version

* Fri Apr 02 2010 J. D. User <jduser@noreply.com> pre-1.10.0-*git*
- SLE11, openSUSE 11.0/1 don't have pidgin/protocols/scalable directory

* Sun Mar 07 2010 pier11 <pier11@operamail.com> pre-1.10.0-*git*
- OBS tests of pre-1.10.0 git-snapshot 4fa20cd65e5be0e469d4aa55d861f11c5b08b816

* Sun Mar 28 2010 J. D. User <jduser@noreply.com> 1.9.1-*git*
- added --enable/--disable build options

* Sun Mar 28 2010 J. D. User <jduser@noreply.com> 1.9.1-*git*
- removed --with-krb5 configure option as it is autodetected now

* Tue Mar 23 2010 J. D. User <jduser@noreply.com> 1.9.1-*git*
- add SVG icon

* Sat Mar 20 2010 J. D. User <jduser@noreply.com> 1.9.1-*git*
- add BR glib2-devel >= 2.12.0

* Wed Mar 17 2010 J. D. User <jduser@noreply.com> 1.9.1-*git*
- add tests to build

* Tue Mar 16 2010 J. D. User <jduser@noreply.com> 1.9.1
- update to 1.9.1

* Thu Mar 11 2010 J. D. User <jduser@noreply.com> 1.9.0-*git*
- add BR libxml2-devel

* Wed Mar 10 2010 pier11 <pier11@operamail.com> 1.9.0
- release
- dropped SLE 10 due to libpurple min version increase
- updated target distros in comment line

* Mon Mar 08 2010 J. D. User <jduser@noreply.com> 1.9.0-*git*
- increased libpurple build requisite to >= 2.4.0

* Sun Mar 07 2010 pier11 <pier11@operamail.com> pre-1.9.0-*git*
- OBS tests of pre-1.9.0 git-snapshot 61ea0856855483b9e18f23a87afe47437e526f0e

* Sun Mar 07 2010 J. D. User <jduser@noreply.com> 1.8.1-*git*
- sync with RPM SPEC from contrib/rpm

* Sun Feb 08 2010 pier11 <pier11@operamail.com> 1.8.0
- source is an original 1.8.0 with patch: git(upstream) 9c34cc3557daa3d61a002002492c71d0343c8cae
- temp hack - renamed source in spec from .bz2 to .gz as the latter was prepared with the patch. 

* Sun Nov 22 2009 pier11 <pier11@operamail.com> 1.7.1
- reinstated enable-quality-check

* Wed Nov 04 2009 John Beranek <john@redux.org.uk> 1.7.0
- Spec file modifications to allow SLES/D 10 and Mandriva 2009.1 builds

* Tue Nov 03 2009 John Beranek <john@redux.org.uk> 1.7.0
- Spec file modifications for openSUSE build service

* Sun Oct 11 2009 J. D. User <jduser@noreply.com> 1.6.3-*git*
- move non-Pidgin files to new sub-package purple-sipe

* Sun Oct 11 2009 J. D. User <jduser@noreply.com> 1.6.3-*git*
- remove directory for emoticon theme icons

* Sun Oct 11 2009 J. D. User <jduser@noreply.com> 1.6.3-*git*
- libpurple protocol plugins are located under %%{_libdir}/purple-2

* Mon Sep 28 2009 J. D. User <jduser@noreply.com> 1.6.3-*git*
- added directory for emoticon theme icons

* Wed Sep 09 2009 J. D. User <jduser@noreply.com> 1.6.3
- update to 1.6.3

* Fri Aug 28 2009 J. D. User <jduser@noreply.com> 1.6.2-*git*
- reduce libpurple-devel requirement to >= 2.3.1

* Mon Aug 24 2009 J. D. User <jduser@noreply.com> 1.6.2
- update to 1.6.2

* Fri Aug 21 2009 J. D. User <jduser@noreply.com> 1.6.1-*git*
- reduce libpurple-devel requirement to >= 2.4.1

* Mon Aug 17 2009 J. D. User <jduser@noreply.com> 1.6.1-*git*
- com_err.h only required for kerberos

* Tue Aug 11 2009 J. D. User <jduser@noreply.com> 1.6.0-*git*
- require libpurple-devel >= 2.5.0

* Sun Aug 09 2009 J. D. User <jduser@noreply.com> 1.6.0-*git*
- refactor configure parameters
- make kerberos configurable
- don't hard code prefix for git builds

* Sun Aug 09 2009 J. D. User <jduser@noreply.com> 1.6.0-*git*
- removed unnecessary zlib-devel

* Sat Aug 08 2009 J. D. User <jduser@noreply.com> 1.6.0-*git*
- fix prefix for git builds

* Sat Aug 01 2009 J. D. User <jduser@noreply.com> 1.6.0-*git*
- append -Wno-unused-parameter for GCC <4.4 compilation errors

* Thu Jul 30 2009 J. D. User <jduser@noreply.com> 1.6.0-*git*
- remove duplicate GPL2

* Thu Jul 30 2009 J. D. User <jduser@noreply.com> 1.6.0-*git*
- use "--with git" to build from git
- corrected download URL for release archive
- add missing BR gettext-devel

* Wed Jul 29 2009 J. D. User <jduser@noreply.com> 1.6.0-*git*
- use default rpmbuild CFLAGS also for git builds
- merge with SPEC files created by mricon & jberanek

* Tue Jul 28 2009 J. D. User <jduser@noreply.com> 1.6.0-*git*
- initial RPM SPEC example generated
