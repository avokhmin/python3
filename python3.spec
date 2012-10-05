%define docver  3.2.3
%define dirver  3.2
%define familyver 3

%define lib_major	%{dirver}
%define lib_name_orig	libpython%{familyver}
%define lib_name	%mklibname python %{lib_major}
%define develname	%mklibname python3 -d

%ifarch %{ix86} x86_64 ppc
%bcond_without	valgrind
%else
%bcond_with	valgrind
%endif
Summary:	An interpreted, interactive object-oriented programming language
Name:		python3
Version:	3.2.3
Release:	6
License:	Modified CNRI Open Source License
Group:		Development/Python

Source:		http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.xz
Source1:	http://www.python.org/ftp/python/doc/%{docver}/python-%{docver}-docs-html.tar.bz2
Source2:	python3.macros
#Source4:	python-mode-1.0.tar.bz2

Patch0:		python-3.1.2-module-linkage.patch
Patch1:		python3-3.2.3-fdr-lib64.patch
Patch2:		python3-3.2.3-fdr-lib64-fix-for-test_install.patch
Patch3:		python-3.2-CVE-2012-2135.patch
Patch4:		python-3.2-bug14579-tests.diff

URL:		http://www.python.org/
Conflicts:	tkinter3 < %{version}
Conflicts:	%{lib_name}-devel < 3.1.2-4
Conflicts:	%{develname} < 3.2.2-3
Requires:	%{lib_name} = %{version}
BuildRequires:	blt
BuildRequires:	db-devel
BuildRequires:	pkgconfig(expat)
BuildRequires:	gdbm-devel
BuildRequires:	gmp-devel
BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	readline-devel
BuildRequires:	termcap-devel
BuildRequires:	tcl tcl-devel
BuildRequires:	tk tk-devel
BuildRequires:	autoconf
BuildRequires:	bzip2-devel
BuildRequires:	pkgconfig(sqlite3)
# uncomment once the emacs part no longer conflict with python 2.X
#BuildRequires:	emacs
#BuildRequires:	emacs-bin
%if %{with valgrind}
BuildRequires:	valgrind-devel
%endif
Provides:	%{name} = %{version}
Provides:	python(abi) = %{dirver}
Provides:	/usr/bin/python%{dirver}mu


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
Requires:	%{name} = %{version}
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
Group:		Development/Python
Requires:	%{name} = %{version}
Requires:	xdg-utils
BuildArch:	noarch

%description	docs
The python-docs package contains documentation on the Python
programming language and interpreter.  The documentation is provided
in ASCII text files and in LaTeX source files.

Install the python-docs package if you'd like to use the documentation
for the Python language.

%package -n	tkinter3
Summary:	A graphical user interface for the Python scripting language
Group:		Development/Python
Requires:	%{name} = %{version}
Requires:	tcl tk

%description -n	tkinter3
The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.

%package -n	tkinter3-apps
Summary:	Various applications written using tkinter
Group:		Development/Python
Requires:	tkinter3

%description -n	tkinter3-apps
Various applications written using tkinter

%prep
%setup -qn Python-%{version}
%patch0 -p0 -b .link
%patch3 -p1 -b .CVE-2012-2135
%patch4 -p1 -b .bug14579-tests

%if "%{_lib}" == "lib64"
%patch1 -p1 -b .lib64
%patch2 -p1
%endif

# docs
mkdir html
bzcat %{SOURCE1} | tar x  -C html

find . -type f -print0 | xargs -0 perl -p -i -e 's@/usr/local/bin/python@/usr/bin/python3@'

cat > README.mga << EOF
Python interpreter support readline completion by default.
This is only used with the interpreter. In order to remove it,
you can :
1) unset PYTHONSTARTUP when you login
2) create a empty file \$HOME/.pythonrc.py
3) change %{_sysconfdir}/pythonrc.py
EOF

%build
rm -f Modules/Setup.local

export OPT="%{optflags} -g"

# to fix curses module build
# https://bugs.mageia.org/show_bug.cgi?id=6702
export CFLAGS="%{optflags} -I/usr/include/ncursesw"
export CPPFLAGS="%{optflags} -I/usr/include/ncursesw"

autoreconf -vfi
%configure2_5x	--with-threads \
		--enable-ipv6 \
		--with-wide-unicode \
		--with-dbmliborder=gdbm \
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
mkdir -p %{buildroot}%{_prefix}/lib/python%{dirver}

# fix Makefile to get rid of reference to distcc
perl -pi -e "/^CC=/ and s/distcc/gcc/" Makefile

# set the install path
echo '[install_scripts]' >setup.cfg
echo 'install_dir='"%{buildroot}%{_bindir}" >>setup.cfg

# python is not GNU and does not know fsstd
mkdir -p %{buildroot}%{_mandir}
%makeinstall_std LN="ln -sf"

(cd %{buildroot}%{_libdir}; ln -sf `ls libpython%{lib_major}*.so.*` libpython%{lib_major}.so)

# fix files conflicting with python2.6
mv %{buildroot}%{_bindir}/2to3 %{buildroot}%{_bindir}/python3-2to3

# conflicts with python2
# # emacs, I use it, I want it
# mkdir -p %{buildroot}%{_datadir}/emacs/site-lisp
# install -m 644 Misc/python-mode.el %{buildroot}%{_datadir}/emacs/site-lisp
# emacs -batch -f batch-byte-compile %{buildroot}%{_datadir}/emacs/site-lisp/python-mode.el
# 
# install -d %{buildroot}%{_sysconfdir}/emacs/site-start.d
# cat <<EOF >%{buildroot}%{_sysconfdir}/emacs/site-start.d/%{name}.el
# (setq auto-mode-alist (cons '("\\\\.py$" . python-mode) auto-mode-alist))
# (autoload 'python-mode "python-mode" "Mode for python files." t)
# EOF

#"  this comment is just here because vim syntax higlighting is confused by the previous snippet of lisp

# install pynche as pynche3
cat << EOF > %{buildroot}%{_bindir}/pynche3
#!/bin/bash
exec %{_libdir}/python%{dirver}/site-packages/pynche/pynche
EOF
rm -f Tools/pynche/*.pyw
cp -r Tools/pynche %{buildroot}%{_libdir}/python%{dirver}/site-packages/

chmod 755 %{buildroot}%{_bindir}/{idle3,pynche3}

ln -f Tools/pynche/README Tools/pynche/README.pynche

%if %{with valgrind}
install Misc/valgrind-python.supp -D %{buildroot}%{_libdir}/valgrind/valgrind-python3.supp
%endif

mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-tkinter3.desktop << EOF
[Desktop Entry]
Name=IDLE
Comment=IDE for Python3
Exec=%{_bindir}/idle3
Icon=development_environment_section
Terminal=false
Type=Application
Categories=Development;IDE;
EOF


cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}-docs.desktop << EOF
[Desktop Entry]
Name=Python documentation
Comment=Python complete reference
Exec=%{_bindir}/xdg-open %{_defaultdocdir}/%{name}-docs/index.html
Icon=documentation_section
Terminal=false
Type=Application
Categories=Documentation;
EOF


# fix non real scripts
#chmod 644 %{buildroot}%{_libdir}/python*/test/test_{binascii,grp,htmlparser}.py*
find %{buildroot} -type f \( -name "test_binascii.py*" -o -name "test_grp.py*" -o -name "test_htmlparser.py*" \) -exec chmod 644 {} \;
# fix python library not stripped
chmod u+w %{buildroot}%{_libdir}/libpython%{lib_major}*.so.1.0 %{buildroot}%{_libdir}/libpython3.so


mkdir -p %{buildroot}%{_sysconfdir}/profile.d/

cat > %{buildroot}%{_sysconfdir}/profile.d/30python.sh << 'EOF'
if [ -f $HOME/.pythonrc.py ] ; then
	export PYTHONSTARTUP=$HOME/.pythonrc.py
else
	export PYTHONSTARTUP=/etc/pythonrc.py
fi

export PYTHONDONTWRITEBYTECODE=1
EOF

cat > %{buildroot}%{_sysconfdir}/profile.d/30python.csh << 'EOF'
if ( -f ${HOME}/.pythonrc.py ) then
	setenv PYTHONSTARTUP ${HOME}/.pythonrc.py
else
	setenv PYTHONSTARTUP /etc/pythonrc.py
endif
setenv PYTHONDONTWRITEBYTECODE 1
EOF

cat > %{buildroot}%{_sysconfdir}/pythonrc.py << EOF
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

%multiarch_includes %{buildroot}/usr/include/python*/pyconfig.h

mkdir -p %{buildroot}%{_sysconfdir}/rpm/macros.d
install -m644 %{SOURCE2} %{buildroot}%{_sysconfdir}/rpm/macros.d/

%files
%doc README.mga
# conflicts with python2.6
#%config(noreplace) %{_sysconfdir}/emacs/site-start.d/%{name}.el
%{_sysconfdir}/rpm/macros.d/*.macros
%{_sysconfdir}/profile.d/*
%config(noreplace) %{_sysconfdir}/pythonrc.py
%{_includedir}/python*/pyconfig.h
%{multiarch_includedir}/python*/pyconfig.h

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
%{_libdir}/libpython*.so.1*

%files -n %{develname}
%{_libdir}/libpython*.so
%{_includedir}/python*
%{_libdir}/python*/config-%{dirver}*
%{_libdir}/python*/test/
%{_bindir}/python%{dirver}*-config
%{_bindir}/python%{familyver}-config
%{_libdir}/pkgconfig/python*.pc
%exclude %{_includedir}/python*/pyconfig.h
%exclude %{_libdir}/python*/config*/Makefile

%files docs
%doc html/*/*
%{_datadir}/applications/mandriva-%{name}-docs.desktop

%files -n tkinter3
%{_libdir}/python*/tkinter/
%{_libdir}/python*/idlelib
%{_libdir}/python*/site-packages/pynche
%{_libdir}/python*/lib-dynload/_tkinter.*.so

%files -n tkinter3-apps
%{_bindir}/idle3*
%{_bindir}/pynche3
%{_datadir}/applications/mandriva-tkinter3.desktop



%changelog

* Wed Aug 08 2012 luigiwalser <luigiwalser> 3.2.3-5.mga3
+ Revision: 280050
- add patch from OpenSuSE to fix CVE-2012-2135 (patch 3)
- add upstream patch adding tests to testsuite associated w/CVE (patch 4)

* Mon Jul 30 2012 tv <tv> 3.2.3-4.mga3
+ Revision: 276244
- rebuild for db-5.3

* Thu Jul 05 2012 wally <wally> 3.2.3-3.mga3
+ Revision: 268245
- fix curses module build (mga#6702)

* Tue Jul 03 2012 kamil <kamil> 3.2.3-2.mga3
+ Revision: 266996
- add P2 fdr-lib64-fix-for-test_install.patch
- sync P1 with Fedora and fix x86_64 bugs (mga#6664)

* Sat Apr 14 2012 fwang <fwang> 3.2.3-1.mga2
+ Revision: 230764
- update lib64 patch
- new version 3.2.3

* Mon Feb 20 2012 guillomovitch <guillomovitch> 3.2.2-3.mga2
+ Revision: 211298
- don't hardcode pyconfig.h location in lib64 path
- ship pyconfig.h in main package, not just multiarch wrapper
- spec cleanup

* Mon Dec 05 2011 fwang <fwang> 3.2.2-2.mga2
+ Revision: 176932
- add upstream patch to recognize gdbm 1.9 magic value
- build with gdbm
- rebuild for new gdbm

* Mon Sep 05 2011 fwang <fwang> 3.2.2-1.mga2
+ Revision: 138550
- new version 3.2.2

* Fri Sep 02 2011 tv <tv> 3.2.1-2.mga2
+ Revision: 137805
- make the huge doc subpackage be noarch

* Tue Jul 12 2011 fwang <fwang> 3.2.1-1.mga2
+ Revision: 122718
- use ln -sf always
- update file list
- really rediff lib64 patch
- rediff lib64 patch
- new version 3.2.1

* Sat Jul 02 2011 fwang <fwang> 3.2-6.mga2
+ Revision: 117326
- rebuild for new tcl

* Tue Jun 28 2011 fwang <fwang> 3.2-5.mga2
+ Revision: 115157
- add provides for binary

* Tue Jun 07 2011 dmorgan <dmorgan> 3.2-4.mga2
+ Revision: 101527
- imported package python3

