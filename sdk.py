import pystache
import sys
import os
import errno
import shutil
import simplejson

from base.pom import Pom

tiles = {


}


def command():
    data = {}
    data["groupId"] = raw_input("groupId: ")
    """
    data["artifactId"] = raw_input("artifactId: ")
    data["version"] = raw_input("version: ")
    data["name"] = raw_input("name: ")
    data["clientUrl"] = raw_input("clienturl: ")
    data["port"] = raw_input("port: ")
    data["appContext"] = raw_input("appContext: ")
    """

    package_path = "src/main/java/" + data["groupId"].replace(".", "/")
    print package_path

    if not os.path.exists(package_path):
        os.makedirs(package_path)

    if not os.path.exists("src/main/resources"):
        os.makedirs("src/main/resources")

    return data


def init():
#    create_base_dir()
    add_tile("tile-table",
             "MyExampleTableList",
             "my-table-tile",
             "com.ms.jive.addon",
             "http://localhost",
             "service")

    print "----------------------"


def create_base_dir():
    root_path = os.path.dirname(__file__)
    src = root_path + "/dir_structure/src"
    dest = os.getcwd() + "/src"
    copy_dir(src, dest)
    print "##################"


def add_tile(style, class_name, tile_name, package, service_url, app_context):
    print "Add tile"
    root_path = os.path.dirname(__file__) + "/styles/" + style
    tile_class_path = root_path + "/Example.java"
    tile_definition_path = root_path + "/definition.json"
    tile_class = read_file(tile_class_path)
    tile_definition = read_file(tile_definition_path)
    tile_class = pystache.render(tile_class, {
        "package": package,
        "class_name": class_name,
        "tile_name": tile_name
    })

    tile_definition = pystache.render(tile_definition, {
        "tile_name": tile_name,
        "tile_style": style,
        "service_url": service_url,
        "app_context": app_context
    })

    definition = load_definition()
    definition["tiles"].append(tile_definition)
    update_definition(definition)


def load_definition():
    """update definition file when you add new component"""
    path = os.getcwd() + "/src/main/extension/definition.json"
    print path
    return simplejson.load(file(path))

def update_definition(new_definition):
    path = os.getcwd() + "/src/main/extension/definition.json"
    with open(path, "w") as f:
        simplejson.dump(new_definition, f)


def read_file(path):
    with open(path) as f:
        content = f.read()

    return content


def save_file(path):
    pass


def copy_dir(src, dest):
    print "src is %s" % src
    print "dest is %s" % dest
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print "dir not copied. Error %s" % e

