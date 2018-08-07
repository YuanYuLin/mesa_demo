import ops
import iopc

TARBALL_FILE="mesa-demos-8.4.0.tar.bz2"
TARBALL_DIR="mesa-demos-8.4.0"
INSTALL_DIR="mesa-demo-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
tmp_include_dir = ""
dst_include_dir = ""
dst_lib_dir = ""
dst_usr_local_lib_dir = ""
PKG_WAYLAND="wayland"

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global tmp_include_dir
    global dst_include_dir
    global dst_lib_dir
    global dst_usr_local_lib_dir
    global src_pkgconfig_dir
    global dst_pkgconfig_dir
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    tmp_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")
    dst_usr_local_lib_dir = ops.path_join(install_dir, "usr/local/lib")
    src_pkgconfig_dir = ops.path_join(pkg_path, "pkgconfig")
    dst_pkgconfig_dir = ops.path_join(install_dir, "pkgconfig")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_LIBDIR", ops.path_join(iopc.getSdkPath(), "pkgconfig")))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_SYSROOT_DIR", iopc.getSdkPath()))

    cc_sysroot = ops.getEnv("CC_SYSROOT")
    cflags = ""
    cflags += " -I" + ops.path_join(cc_sysroot, 'usr/include')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm/libdrm')

    ldflags = ""
    ldflags += " -L" + ops.path_join(cc_sysroot, 'lib')
    ldflags += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    ldflags += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')

    libs = ""
    libs += " -lffi -lxml2 -lexpat -ldrm"
    #ops.exportEnv(ops.setEnv("LDFLAGS", ldflags))
    #ops.exportEnv(ops.setEnv("CFLAGS", cflags))
    #ops.exportEnv(ops.setEnv("LIBS", libs))

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarBz2(tarball_pkg, output_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    extra_conf = []
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("V=1")
    extra_conf.append("--disable-x11")
    extra_conf.append("--disable-gles1")
    extra_conf.append("--enable-gles2")
    extra_conf.append("--enable-egl")
    extra_conf.append("--enable-libdrm")
    #extra_conf.append("--enable-vg")

    cc_sysroot = ops.getEnv("CC_SYSROOT")
    cflags = ""
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/mesa')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libglu')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm/libdrm')
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/libdrm/libkms')
    cflags += " -DMESA_EGL_NO_X11_HEADERS"

    libs = ""
    libs += " -L" + ops.path_join(cc_sysroot, 'lib')
    libs += " -L" + ops.path_join(cc_sysroot, 'usr/lib')
    libs += " -L" + ops.path_join(iopc.getSdkPath(), 'lib')
    libs += " -ldrm -lEGL -lglapi -lGLESv2 -lOSMesa -lGLU -lgbm -lxml2 -lexpat -lz -lffi -lfreetype"

    extra_conf.append('GL_CFLAGS=' + cflags)
    extra_conf.append('GL_LIBS=' + libs)
    extra_conf.append('EGL_CFLAGS=' + cflags)
    extra_conf.append('EGL_LIBS=' + libs)
    extra_conf.append('GLESV2_CFLAGS=' + cflags)
    extra_conf.append('GLESV2_LIBS=' + libs)
    extra_conf.append('DRM_CFLAGS=' + cflags)
    extra_conf.append('DRM_LIBS=' + libs)
    extra_conf.append('GBM_CFLAGS=' + cflags)
    extra_conf.append('GBM_LIBS=' + libs)
    extra_conf.append('OSMESA_CFLAGS=' + cflags)
    extra_conf.append('OSMESA_LIBS=' + libs)

    #extra_conf.append('GLEW_CFLAGS=' + cflags)
    #extra_conf.append('GLEW_LIBS=' + libs)
    extra_conf.append('GLU_CFLAGS=' + cflags)
    extra_conf.append('GLU_LIBS=' + libs)
    extra_conf.append('FREETYPE2_CFLAGS=' + libs)
    extra_conf.append('FREETYPE2_LIBS=' + libs)

    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    print "Test " + ops.getEnv("PATH")
    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(install_dir)
    ops.mkdir(dst_lib_dir)
    ops.mkdir(dst_usr_local_lib_dir)
    libegl = "libEGL.so.1.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libegl), dst_lib_dir)
    ops.ln(dst_lib_dir, libegl, "libEGL.so.1.0")
    ops.ln(dst_lib_dir, libegl, "libEGL.so.1")
    ops.ln(dst_lib_dir, libegl, "libEGL.so")

    libglesv2 = "libGLESv2.so.2.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libglesv2), dst_lib_dir)
    ops.ln(dst_lib_dir, libglesv2, "libGLESv2.so.2.0")
    ops.ln(dst_lib_dir, libglesv2, "libGLESv2.so.2")
    ops.ln(dst_lib_dir, libglesv2, "libGLESv2.so")

    libgbm = "libgbm.so.1.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libgbm), dst_lib_dir)
    ops.ln(dst_lib_dir, libgbm, "libgbm.so.1.0")
    ops.ln(dst_lib_dir, libgbm, "libgbm.so.1")
    ops.ln(dst_lib_dir, libgbm, "libgbm.so")

    libglapi = "libglapi.so.0.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libglapi), dst_lib_dir)
    ops.ln(dst_lib_dir, libglapi, "libglapi.so.0.0")
    ops.ln(dst_lib_dir, libglapi, "libglapi.so.0")
    ops.ln(dst_lib_dir, libglapi, "libglapi.so")

    if iopc.is_selected_package(PKG_WAYLAND):
        libwayland = "libwayland-egl.so.1.0.0"
        ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libwayland), dst_lib_dir)
        ops.ln(dst_lib_dir, libwayland, "libwayland-egl.so.1.0")
        ops.ln(dst_lib_dir, libwayland, "libwayland-egl.so.1")
        ops.ln(dst_lib_dir, libwayland, "libwayland-egl.so")

    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/dri"), dst_usr_local_lib_dir)

    ops.mkdir(tmp_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), tmp_include_dir)

    ops.mkdir(dst_pkgconfig_dir)
    ops.copyto(ops.path_join(src_pkgconfig_dir, '.'), dst_pkgconfig_dir)

    return False

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(ops.path_join(install_dir, "lib"), "."), "lib")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_usr_local_lib_dir, "."), "usr/local/lib")
    iopc.installBin(args["pkg_name"], ops.path_join(tmp_include_dir, "."), dst_include_dir)
    iopc.installBin(args["pkg_name"], ops.path_join(dst_pkgconfig_dir, '.'), "pkgconfig")

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

