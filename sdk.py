import pystache
import sys
import os
import errno
import shutil
import simplejson

from base.pom import Pom

styles = ["app", "tile-table", "tile-list"]

default_name = {
    "app": "sample-app",
    "tile-table": "sample-tile-table",
    "tile-list": "sample-tile-list"
}

validate_cmds = ["create", "list", "help"]

item_descriptions = {
    "app": "A basic Jive App",
    "tile-table": "A basic table tile",
    "tile-list": "A basic list tile"
}

class Generator(object):
    def __init__(self):
        self.cwd = os.getcwd()
        self.sdk_path = os.path.dirname(__file__)
        project_info_path = self.cwd + "/project.info"
        
        if not os.path.isfile(project_info_path):
            project_info = user_input()
            create_base_dir(self.sdk_path, self.cwd, project_info)
            with open(project_info_path, "w+") as f:
                simplejson.dump(project_info, f, indent=2)
        else:
            print "> Already exists, skipping" 

        with open(self.cwd + "/project.info") as f:
            project_info = simplejson.load(f)

        self.package = project_info["groupId"]
        self.package_path = self.package.replace(".", "/")
        self.clienturl = project_info["clienturl"]
        self.appContext = project_info["appContext"]

    def create(self, style, tile_name):
        if style.startswith("tile"):
            class_name = raw_input("please input tile class name:")

            add_tile(style,
                     class_name,
                     tile_name,
                     self.package,
                     self.clienturl, 
                     self.appContext)

        elif style.startswith("app"):
            app_name = raw_input("please input app name")
            add_app()

def copy_pom(cwd, data):
    print "> Generate pom.xml"
    pom = Pom(data)
    renderer = pystache.Renderer()
    new_pom = renderer.render(pom)
    with open(cwd + "/pom.xml", "w+") as f:
        f.write(new_pom)

def user_input():
    data = {}
    data["groupId"] = raw_input("groupId: ")
    data["artifactId"] = raw_input("artifactId: ")
    data["version"] = raw_input("version: ")
    data["name"] = raw_input("name: ")
    data["clienturl"] = raw_input("clienturl: ")
    data["port"] = raw_input("port: ")
    data["appContext"] = raw_input("appContext: ")

    return data

def init():
    args =  sys.argv
    args_length = len(args)
    if args_length <= 1:
        print help()
        sys.exit()

    if args[1] == "create":
        if args_length == 2:
            print help()
            sys.exit()

        style = args[2]
        if style not in styles:
            print style + " not support"
            print "Support styles:"
            print styles
        else:
            for idx in range (3, args_length):
                if args[idx].startswith("--name="):
                    tile_name = args[idx][7:]
                if args[idx].startswith("--force="):
                    pass

            generator = Generator()
            generator.create(style, tile_name)

def help():
    print "Jive Java SDK version 0.1"
    print "usage: jive-sdk <command> <item> [--options]\n"
    print "Available commands:"
    print "   help" + " "*20 + "Display this help page"
    print "   list" + " "*20 + "List the existing items for a category"
    print "   create" + " "*18 + "Create a jive-sdk template or example"

    print ""
    print "Available template item for create command:"
    print "   app" + " "*21 + "A basic Jive app"

    print ""
    print "Available options:"
    print "   --force=<true/false>" + " "*4 + "Whether to overwrite existing data;"
    print "   --name=\"<string>\"" + " "*7 + "Use the specified string for the new item name"



def create_base_dir(sdk_path, cwd, project_info):
    print "> Create basic project structure"
    src = sdk_path + "/dir_structure/src"
    dest = cwd + "/src"
    copy_dir(src, dest)
    #copy_pom(groupId, artifactId, version, clientUrl, port, appContext)
    copy_pom(cwd, project_info)
    copy_default_service("com.ms.jive.addon")
    #TODO ignore if created
    print "##################"

def copy_default_service(package):
    print "> Generating service HealthService.java"
    root_path = os.path.dirname(__file__)
    healthPath = root_path + "/base/HealthService.java"
    healthService = read_file(healthPath)
    healthService = pystache.render(healthService, {
        "package": package   
    })

    path = os.getcwd() + "/src/main/java/" + package.replace(".", "/") + "/service/"
    os.makedirs(path)
    with open(path + "HealthService.java", "a+") as f:
        f.write(healthService)

def add_app(app_name, title="app demo", description="demo app", author=""):
    pass

def add_tile(style, class_name, tile_name, package, service_url, app_context):
    print "Add tile"
    root_path = os.path.dirname(__file__)
    style_path = root_path + "/styles/" + style
    tile_class_path = style_path + "/Example.java"
    tile_definition_path = style_path + "/definition.json"
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
    definition["tiles"].append(simplejson.loads(tile_definition))
    update_definition(definition)

    # Add tile java class
    #TODO check if exist
    tile_dest = os.getcwd() + "/src/main/java/" + package.replace(".", "/") + "/tile/"
    if not os.path.exists(tile_dest):
        os.makedirs(tile_dest)
    with open(tile_dest + "/" + class_name + ".java", "a+") as f:
        f.write(tile_class)

    #Register bean
    appContext_path = root_path + "/base/applicationContext.xml"
    appContext = read_file(appContext_path)
    bean = "<bean id=\"" + tile_name + "\" class="
    bean += "\"" + package + ".tile." + class_name + "\"" + " scope=\"singleton\">"
    bean += "\n    <!-- insert bean -->"
    ref = "<ref bean=\"" + tile_name + "\">\n        <!-- insert ref -->"
    appContext = appContext.replace("{{package}}", package)
    appContext = appContext.replace("<!-- insert bean -->", bean)
    appContext = appContext.replace("<!-- insert ref -->", ref)

    generate_appContext(appContext)


    # Add tile front side files
    tile_front_path = os.getcwd() + "/src/main/webapp/tiles/" + tile_name
    #os.makedirs(tile_front_path)
    copy_dir(style_path + "/public/", tile_front_path)


def load_definition():
    """update definition file when you add new component"""
    path = os.getcwd() + "/src/main/extension/definition.json"
    print path
    return simplejson.load(file(path))

def update_definition(new_definition):
    path = os.getcwd() + "/src/main/extension/definition.json"
    with open(path, "w") as f:
        simplejson.dump(new_definition, f, indent=2)

def generate_appContext(new_appContext):
    path = os.getcwd() + "/src/main/resources/applicationContext.xml"
    with open(path, "w") as f:
        f.write(new_appContext)


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

