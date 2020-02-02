
class ops():
    def __init__(self):
        pass
    def remove(self, obj, name):
        pass
class bobj():
    name = None
    def __init__(self, name):
        self.name = name
class objects(list):
    def __init__(self):
        pass
class scene():
    frame_start = 0
    frame_end = 250
class data():
    objects = objects()
    scenes = [scene()]
    def __init__(self):
        pass
class libraries():
    def __init__(self):
        pass
class wm():
    def __init__(self):
        pass
class app():
    version = (2, 79, 0)
class bpy():
    ops = ops()
    data = data()
    libraries = libraries()
    wm = wm()
    app = app()
    def __init__(self):
        pass
    def O(self):
        return self.ops
    def D(self):
        return self.data
    def L(self):
        return self.O().libraries
    def W(self):
        return self.L().wm

    def load(self, blend_file_path, link=False):
        return 'mock-from' 'mock_to'
    
    def save_as_mainfile(self, filepath):
        return True
    def getObjectList(self):
        return [ 'mock_object_1', 'mock_object_2' ]
