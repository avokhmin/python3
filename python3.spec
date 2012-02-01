%define docver  3.2.1
%define dirver  3.2
%define familyver 3

%define lib_major	%{dirver}
%define lib_name_orig	libpython%{familyver}
%define lib_name	%mklibname python %{lib_major}
%define develname	%mklibname python3 -d

%define _requires_exceptions /usr/bin/python%{dirver}

%ifarch %{ix86} x86_64 ppc
%bcond_without	valgrind
%else
%bcond_with	valgrind
%endif
Summary:	An interpreted, interactive object-oriented programming language
Name:		python3
Version:	3.2.1
Release:	%mkrel 2
License:	Modified CNRI Open Source License
Group:		Development/Python

Source:		http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.xz
Source1:	http://www.python.org/ftp/python/doc/%{docver}/python-%{docver}-docs-html.tar.bz2
Source2:	python3.macros
#Source4:	python-mode-1.0.tar.bz2

Patch0:		python-3.1.2-module-linkage.patch
Patch1:		python3-lib64.patch
# fix http://bugs.python.org/issue6244
# and https://qa.mandriva.com/show_bug.cgi?id=56260
Patch2:     python-2.5-tcl86.patch
# backported from svn
Patch3:		python3-disable-pymalloc-on-valgrind.patch

URL:		http://www.python.org/
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Conflicts:	tkinter3 < %{version}
Conflicts:	%{lib_name}-devel < 3.1.2-4
Conflicts:	%{develname} < 3.2-4
Requires:	%{lib_name} = %{version}
BuildRequires:	blt
BuildRequires:	db-devel
BuildRequires:	expat-devel
BuildRequires:	gdbm-devel
BuildRequires:	gmp-devel
BuildRequires:	ncursesw-devel
BuildRequires:	openssl-devel
BuildRequires:	readline-devel
BuildRequires:	termcap-devel
BuildRequires:	tcl tcl-devel
BuildRequires:	tk tk-devel
BuildRequires:	autoconf automake
BuildRequires:  bzip2-devel
BuildRequires:  sqlite3-devel
# uncomment once the emacs part no longer conflict with python 2.X
#BuildRequires:	emacs
#BuildRequires:	emacs-bin
%if %{with valgrind}
BuildRequires:	valgrind-devel
%endif
Provides:       %{name} = %version
Provides:	python(abi) = %{dirver}
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root


%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that
need a programmable interface. This package contains most of the
standard Python modules, as well as modules for interfacing to the
Tix widget set for Tk and RPM.

Note that documentation for Python is provided in the python-docs
package.

%package -n	%{lib_name}
Summary:	Shared libraries for Python %{version}
Group:		System/Libraries

%description -n	%{lib_name}
This packages contains Python shared object library.  Python is an
interpreted, interactive, object-oriented programming language often
compared to Tcl, Perl, Scheme or Java.

%package -n	%{develname}
Summary:	The libraries and header files needed for Python development
Group:		Development/Python
Requires:	%{name} = %version
Requires:	%{lib_name} = %{version}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{lib_name_orig}-devel = %{version}-%{release}
Obsoletes:	%{_lib}python3.1-devel < %{version}
Obsoletes:	%{_lib}python3.2-devel < %{version}-%{release}

%description -n	%{develname}
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install %{develname} if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%package	docs
Summary:	Documentation for the Python programming language
Requires:	%name = %version
Requires:	xdg-utils
Group:		Development/Python

%description	docs
The python-docs package contains documentation on the Python
programming language and interpreter.  The documentation is provided
in ASCII text files and in LaTeX source files.

Install the python-docs package if you'd like to use the documentation
for the Python language.

%package -n	tkinter3
Summary:	A graphical user interface for the Python scripting language
Group:		Development/Python
Requires:	%name = %version
Requires:       tcl tk

%description -n	tkinter3
The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.

%package -n	tkinter3-apps
Summary:	Various applications written using tkinter
Group:		Development/Python
Requires:   tkinter3

%description -n	tkinter3-apps
Various applications written using tkinter

%prep
%setup -qn Python-%{version}
%patch0 -p0 -b .link
%patch1 -p1 -b .lib64

#patch2 -p1
#patch3 -p1 -b .valgrind~

# docs
mkdir html
bzcat %{SOURCE1} | tar x  -C html

find . -type f -print0 | xargs -0 perl -p -i -e 's@/usr/local/bin/python@/usr/bin/python3@'

cat > README.mdv << EOF
Python interpreter support readline completion by default.
This is only used with the interpreter. In order to remove it,
you can :
1) unset PYTHONSTARTUP when you login
2) create a empty file \$HOME/.pythonrc.py
3) change %{_sysconfdir}/pythonrc.py
EOF

%build
rm -f Modules/Setup.local

OPT="$RPM_OPT_FLAGS -g"
export OPT
autoreconf
%configure2_5x	--with-threads \
		--enable-ipv6 \
		--with-wide-unicode \
		--enable-shared \
%if %{with valgrind}
		--with-valgrind
%endif

# fix build
#perl -pi -e 's/^(LDFLAGS=.*)/$1 -lstdc++/' Makefile
# (misc) if the home is nfs mounted, rmdir fails due to delay
export TMP="/tmp" TMPDIR="/tmp"
%make LN="ln -sf"

%check
# (misc) if the home is nfs mounted, rmdir fails
export TMP="/tmp" TMPDIR="/tmp"

# all tests must pass
# (misc, 28/11/2006) test_shutil is causing problem in iurt, it seems to remove /tmp,
# which make other test fail
# (misc, 11/12/2006) test_pyexpat is icrashing, seem to be done on purpose ( http://python.org/sf/1296433 )
# (misc, 11/12/2006) test_minidom is not working anymore, something changed either on my computer
# or elsewhere.
# (misc, 11/12/2006) test_sax fail too, will take a look later
# (misc, 21/08/2007) test_string and test_str segfault, test_unicode, test_userstring, I need to pass the package as a security update
# (eugeni, 21/07/2009) test_distutils fails with python3.1 due to ld error
# (eugeni, 22/07/2009) test_mailbox fails on the BS
# (eugeni, 17/08/2009) test_telnetlib fails with a connection reset by peer message
# test test_sax failed -- 1 of 44 tests failed: test_xmlgen_attr_escape
make test TESTOPTS="-w -l -x test_linuxaudiodev -x test_nis -x test_shutil -x test_pyexpat -x test_minidom -x test_sax -x test_string -x test_str -x test_unicode -x test_userstring -x test_bytes -x test_distutils -x test_mailbox -x test_ioctl -x test_telnetlib"

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %buildroot%{_prefix}/lib/python%{dirver}

# fix Makefile to get rid of reference to distcc
perl -pi -e "/^CC=/ and s/distcc/gcc/" Makefile

# set the install path
echo '[install_scripts]' >setup.cfg
echo 'install_dir='"${RPM_BUILD_ROOT}/usr/bin" >>setup.cfg

# python is not GNU and does not know fsstd
mkdir -p $RPM_BUILD_ROOT%{_mandir}
%makeinstall_std LN="ln -sf"

(cd $RPM_BUILD_ROOT%{_libdir}; ln -sf `ls libpython%{lib_major}*.so.*` libpython%{lib_major}.so)

# fix files conflicting with python2.6
mv $RPM_BUILD_ROOT/%{_bindir}/2to3 $RPM_BUILD_ROOT/%{_bindir}/python3-2to3

# conflicts with python2
# # emacs, I use it, I want it
# mkdir -p $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp
# install -m 644 Misc/python-mode.el $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp
# emacs -batch -f batch-byte-compile $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/python-mode.el
# 
# install -d $RPM_BUILD_ROOT%{_sysconfdir}/emacs/site-start.d
# cat <<EOF >$RPM_BUILD_ROOT%{_sysconfdir}/emacs/site-start.d/%{name}.el
# (setq auto-mode-alist (cons '("\\\\.py$" . python-mode) auto-mode-alist))
# (autoload 'python-mode "python-mode" "Mode for python files." t)
# EOF

#"  this comment is just here because vim syntax higlighting is confused by the previous snippet of lisp

# install pynche as pynche3
cat << EOF > $RPM_BUILD_ROOT%{_bindir}/pynche3
#!/bin/bash
exec %{_libdir}/python%{dirver}/site-packages/pynche/pynche
EOF
rm -f Tools/pynche/*.pyw
cp -r Tools/pynche $RPM_BUILD_ROOT%{_libdir}/python%{dirver}/site-packages/

chmod 755 $RPM_BUILD_ROOT%{_bindir}/{idle3,pynche3}

ln -f Tools/pynche/README Tools/pynche/README.pynche

%if %{with valgrind}
install Misc/valgrind-python.supp -D $RPM_BUILD_ROOT%{_libdir}/valgrind/valgrind-python3.supp
%endif

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-tkinter3.desktop << EOF
[Desktop Entry]
Name=IDLE
Comment=IDE for Python3
Exec=%{_bindir}/idle3
Icon=development_environment_section
Terminal=false
Type=Application
Categories=Development;IDE;
EOF


cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}-docs.desktop << EOF
[Desktop Entry]
Name=Python documentation
Comment=Python complete reference
Exec=%{_bindir}/xdg-open %_defaultdocdir/%{name}-docs/index.html
Icon=documentation_section
Terminal=false
Type=Application
Categories=Documentation;
EOF


# fix non real scripts
chmod 644 $RPM_BUILD_ROOT%{_libdir}/python*/test/test_{binascii,grp,htmlparser}.py*
# fix python library not stripped
chmod u+w $RPM_BUILD_ROOT%{_libdir}/libpython%{lib_major}*.so.1.0 $RPM_BUILD_ROOT%{_libdir}/libpython3.so


mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/

cat > $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/30python.sh << 'EOF'
if [ -f $HOME/.pythonrc.py ] ; then
	export PYTHONSTARTUP=$HOME/.pythonrc.py
else
	export PYTHONSTARTUP=/etc/pythonrc.py
fi

export PYTHONDONTWRITEBYTECODE=1
EOF

cat > $RPM_BUILD_ROOT/%{_sysconfdir}/profile.d/30python.csh << 'EOF'
if ( -f ${HOME}/.pythonrc.py ) then
	setenv PYTHONSTARTUP ${HOME}/.pythonrc.py
else
	setenv PYTHONSTARTUP /etc/pythonrc.py
endif
setenv PYTHONDONTWRITEBYTECODE 1
EOF

cat > $RPM_BUILD_ROOT%{_sysconfdir}/pythonrc.py << EOF
try:
    # this add completion to python interpreter
    import readline
    import rlcompleter
    # see readline man page for this
    readline.parse_and_bind("set show-all-if-ambiguous on")
    readline.parse_and_bind("tab: complete")
except:
    pass
# you can place a file .pythonrc.py in your home to overrides this one
# but then, this file will not be sourced
EOF

%multiarch_includes $RPM_BUILD_ROOT/usr/include/python*/pyconfig.h

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/rpm/macros.d
install -m644 %{SOURCE2} $RPM_BUILD_ROOT/%{_sysconfdir}/rpm/macros.d/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root, 755)
%doc README.mdv
# conflicts with python2.6
#%config(noreplace) %{_sysconfdir}/emacs/site-start.d/%{name}.el
%{_sysconfdir}/rpm/macros.d/*.macros
%{_sysconfdir}/profile.d/*
%config(noreplace) %{_sysconfdir}/pythonrc.py
%{_includedir}/python*/pyconfig.h
%{_libdir}/python*/config*/Makefile
%exclude %{_libdir}/python*/site-packages/pynche
%exclude %{_libdir}/python*/lib-dynload/_tkinter.*.so

# HACK: build fails without this (TODO: investigate rpm)
%dir %{_libdir}/python*
%{_libdir}/python*/LICENSE.txt
%{_libdir}/python%{dirver}/*.py
%{_libdir}/python%{dirver}/__pycache__
%{_libdir}/python%{dirver}/concurrent
%{_libdir}/python%{dirver}/ctypes
%{_libdir}/python%{dirver}/curses
%{_libdir}/python%{dirver}/dbm
%{_libdir}/python%{dirver}/distutils
%{_libdir}/python%{dirver}/email
%{_libdir}/python%{dirver}/encodings
%{_libdir}/python%{dirver}/html
%{_libdir}/python%{dirver}/http
%{_libdir}/python%{dirver}/importlib
%{_libdir}/python%{dirver}/json
%{_libdir}/python%{dirver}/lib-dynload
%{_libdir}/python%{dirver}/lib2to3
%{_libdir}/python%{dirver}/logging
%{_libdir}/python%{dirver}/multiprocessing
%{_libdir}/python%{dirver}/plat-linux2
%{_libdir}/python%{dirver}/pydoc_data
%{_libdir}/python%{dirver}/site-packages
%{_libdir}/python%{dirver}/sqlite3
%{_libdir}/python%{dirver}/turtledemo
%{_libdir}/python%{dirver}/unittest
%{_libdir}/python%{dirver}/urllib
%{_libdir}/python%{dirver}/wsgiref*
%{_libdir}/python%{dirver}/xml
%{_libdir}/python%{dirver}/xmlrpc
%{_bindir}/pydoc3*
%{_bindir}/python3*
%{_bindir}/2to3-%{dirver}
%exclude %{_bindir}/python*config
#%{_datadir}/emacs/site-lisp/*
%{_mandir}/man*/*
%if %{with valgrind}
%{_libdir}/valgrind/valgrind-python3.supp
%endif

%files -n %{lib_name}
%defattr(-,root,root)
%{_libdir}/libpython*.so.1*

%files -n %{develname}
%defattr(-, root, root, 755)
%{_libdir}/libpython*.so
%multiarch_includedir/python*/pyconfig.h
%{_includedir}/python*
%{_libdir}/python*/config-%{dirver}*
%{_libdir}/python*/test/
%{_bindir}/python%{dirver}*-config
%{_bindir}/python%{familyver}-config
%{_libdir}/pkgconfig/python*.pc
%exclude %{_includedir}/python*/pyconfig.h
%exclude %{_libdir}/python*/config*/Makefile

%files docs
%defattr(-,root,root,755)
%doc html/*/*
%{_datadir}/applications/mandriva-%{name}-docs.desktop

%files -n tkinter3
%defattr(-, root, root, 755)
%{_libdir}/python*/tkinter/
%{_libdir}/python*/idlelib
%{_libdir}/python*/site-packages/pynche
%{_libdir}/python*/lib-dynload/_tkinter.*.so

%files -n tkinter3-apps
%defattr(-, root, root, 755)
%{_bindir}/idle3*
%{_bindir}/pynche3
%{_datadir}/applications/mandriva-tkinter3.desktop

%if %mdkversion < 200900
%post -n %{lib_name} -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%post -n tkinter3-apps
%update_menus
%endif

%if %mdkversion < 200900
%postun -n tkinter3-apps
%clean_menus
%endif




%changelog
* Sun Aug 14 2011 Funda Wang <fwang@mandriva.org> 3.2.1-2mdv2011.0
+ Revision: 694448
- add requires exception
- redif lib64 patch
- new version 3.2.1

* Mon May 02 2011 Funda Wang <fwang@mandriva.org> 3.2-4
+ Revision: 661885
- update file list
- update file list
- move makefile and pyconfig into main
- more lib64 patch

* Sun Apr 24 2011 Funda Wang <fwang@mandriva.org> 3.2-3
+ Revision: 658191
- rename devel name

* Sat Apr 23 2011 Funda Wang <fwang@mandriva.org> 3.2-2
+ Revision: 656821
- build with wide-unicode

* Sat Apr 23 2011 Funda Wang <fwang@mandriva.org> 3.2-1
+ Revision: 656799
- update file list
- use space
- clean spec file
- rediff lib64 patch
- rediff lib64 patch
- new version 3.2

* Mon Nov 01 2010 Funda Wang <fwang@mandriva.org> 3.1.2-4mdv2011.0
+ Revision: 591289
- move macro into main package

* Sun Oct 31 2010 Funda Wang <fwang@mandriva.org> 3.1.2-3mdv2011.0
+ Revision: 591178
- fix module link
- drop obsoletes swtich
- add python3.macros to ease python3 packaging
- tweak binary name in scripts

* Sat Oct 30 2010 Anssi Hannula <anssi@mandriva.org> 3.1.2-2mdv2011.0
+ Revision: 590324
- add provides on python(abi) (as per Fedora), for automated python
  module dependencies on python version
- workaround rpm issue in filelist to fix build

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - backport disable pymalloc on valgrind from svn

* Thu Apr 22 2010 Michael Scherer <misc@mandriva.org> 3.1.2-1mdv2010.1
+ Revision: 537934
- update to 3.1.2
- fix cruft in lib64 patch

* Sat Apr 17 2010 Michael Scherer <misc@mandriva.org> 3.1.1-9mdv2010.1
+ Revision: 536061
- rebuild for new rpm-mandriva-setup, to fix installation ( #58793 )

* Thu Apr 08 2010 Michael Scherer <misc@mandriva.org> 3.1.1-8mdv2010.1
+ Revision: 533004
- rebuild for new rpm-mandriva-setup

* Thu Mar 25 2010 Michael Scherer <misc@mandriva.org> 3.1.1-7mdv2010.1
+ Revision: 527485
- rebuild to fix upgrade ( due to python-base removal )

* Fri Feb 05 2010 Michael Scherer <misc@mandriva.org> 3.1.1-6mdv2010.1
+ Revision: 501053
- remove BR on emacs as we do not build emacs extension for the moment ( conflict with python 2.x )
- do not add a BuildRequires on emacs, uneeded for the moment
- remove old comment
- use README.mdv, not mdk
- do not obsolete package that does exist
- remove redundant BuildRequires
- do not provides python-base, this should be removed from the distro,
  as there is no subpackage named like this ( more ever, this is likely to
  be a wrong provides, as python 3 is too different from python 2 )

* Sun Jan 17 2010 Michael Scherer <misc@mandriva.org> 3.1.1-5mdv2010.1
+ Revision: 492597
- fix linking to ncursesw, to fix canto segfaulting

* Sun Jan 03 2010 Michael Scherer <misc@mandriva.org> 3.1.1-4mdv2010.1
+ Revision: 486004
- move tkinter module to proper subpackage
- add patch to fix bug 56260, as python do not detect tcl/tk 8.6, by porting the patch from
  regular python package to python 3

* Wed Nov 11 2009 Michael Scherer <misc@mandriva.org> 3.1.1-3mdv2010.1
+ Revision: 464473
- fix file conflict for tkinteer desktop file, as pointed by laurent pointal on bug  55507

* Tue Aug 18 2009 Eugeni Dodonov <eugeni@mandriva.com> 3.1.1-2mdv2010.0
+ Revision: 417514
- updated to 3.1.1

* Fri Jul 24 2009 Bogdano Arendartchuk <bogdano@mandriva.com> 3.1-2mdv2010.0
+ Revision: 399512
- adapted the lib64 patch to py3k

  + Eugeni Dodonov <eugeni@mandriva.com>
    - Packaged python3.
    - Created package structure for python3.

