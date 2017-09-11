import os
import platform
import shutil
import sys

import click

import pyqt5toolsbuild.utils


@click.command()
def main():
    build_venv_bin = os.path.dirname(sys.executable)
    build_python_path = sys.executable
    build_pyqtdeploycli_path = os.path.join(build_venv_bin, 'pyqtdeploycli')

    build = os.environ['TRAVIS_BUILD_DIR']
    deployed_qt = os.path.join(build, 'deployed_qt')
    destination = os.path.join(build, 'pyqt5-tools')
    src_path = os.path.join(build, 'src')
    sysroot = os.path.join(build, 'sysroot')
    native_sysroot = os.path.join(sysroot, 'native')

    os.makedirs(sysroot)
    os.makedirs(native_sysroot)
    os.makedirs(src_path)

    bits = int(platform.architecture()[0][0:2])
    python_major_minor = '{}{}'.format(
        sys.version_info.major,
        sys.version_info.minor
    )

    print('copying {}'.format(deployed_qt))
    print('     to {}'.format(destination))
    shutil.copytree(deployed_qt, destination)

    pyqt5_version = pyqt5toolsbuild.utils.Version.from_string(
        os.environ['PYQT5_VERSION'],
    )
    qt_version = pyqt5toolsbuild.utils.pyqt_to_qt_version(pyqt5_version)

    qt_bin_path = pyqt5toolsbuild.utils.qt_path(qt_version)
    qmake = os.path.join(qt_bin_path, 'qmake.exe')
    make = 'make'

    qt_version = pyqt5toolsbuild.utils.pyqt_to_qt_version(pyqt5_version)
    sip_version = pyqt5toolsbuild.utils.pyqt_to_sip_version(pyqt5_version)

    sip_name, sip_url = pyqt5toolsbuild.utils.sip_name_url(sip_version)
    sip_path = os.path.join(src_path, sip_name)
    native_sip_path = sip_path + '-native'

    pyqt5toolsbuild.utils.extract_zip_url(
        url=sip_url,
        destination=src_path,
    )

    shutil.copytree(sip_path, native_sip_path)

    pyqt5toolsbuild.utils.report_and_check_call(
        command=[
            build_python_path,
            'configure.py',
            '--static',
            '--sysroot={}'.format(native_sysroot),
            '--platform=linux-g++',
            '--target-py-version={}'.format('.'.join(python_major_minor)),
        ],
        cwd=native_sip_path,
    )
    pyqt5toolsbuild.utils.report_and_check_call(
        command=[
            make,
        ],
        cwd=native_sip_path,
        env=os.environ,
    )
    pyqt5toolsbuild.utils.report_and_check_call(
        command=[
            make,
            'install',
        ],
        cwd=native_sip_path,
        env=os.environ,
    )

    pyqt5toolsbuild.utils.report_and_check_call(
        command=[
            build_pyqtdeploycli_path,
            '--package', 'sip',
            '--target', 'linux-{}'.format(bits),
            'configure',
        ],
        cwd=sip_path,
    )

    pyqt5toolsbuild.utils.report_and_check_call(
        command=[
            build_python_path,
            'configure.py',
            '--static',
            '--sysroot={}'.format(sysroot),
            '--no-tools',
            '--use-qmake',
            '--configuration=sip-win.cfg',
            '--platform=linux-g++',
            '--target-py-version={}'.format('.'.join(python_major_minor)),
        ],
        cwd=sip_path,
    )

    pyqt5toolsbuild.utils.report_and_check_call(
        command=[
            qmake,
        ],
        cwd=sip_path,
        env=os.environ,
    )

    pyqt5toolsbuild.utils.report_and_check_call(
        command=[
            make,
        ],
        cwd=sip_path,
        env=os.environ,
    )

    pyqt5toolsbuild.utils.report_and_check_call(
        command=[
            make,
            'install',
        ],
        cwd=sip_path,
        env=os.environ,
    )
