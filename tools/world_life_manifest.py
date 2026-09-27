import sys
import xml.etree.ElementTree as ET

ANDROID_NS = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", ANDROID_NS)

path, label, version = sys.argv[1:4]
tree = ET.parse(path)
root = tree.getroot()
root.set("{" + ANDROID_NS + "}label", label)
root.set("{" + ANDROID_NS + "}versionName", version)
tree.write(path, encoding="utf-8", xml_declaration=True)
