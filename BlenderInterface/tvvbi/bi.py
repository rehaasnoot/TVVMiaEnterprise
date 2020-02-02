# Note: this is the interface between the agent and blender python api
# Current assumptions:
# blagent, tvvmia and dependencies are accessible.
#import bpy
#from tvvbpymain import TVVBaseParameters, BPYBase
#from tvvmain import TVVBaseParameters
import io
import os

DEBUG = False
if os.environ.get("DEBUG") == "True":
    DEBUG = True

class TVVMidoFile(io.BufferedReader):
    MAX_MIDI_DATA_SIZE = 65000
    FILE_POS = 0
    STREAM = None
    def __init__(self, file_object):
        self.STREAM = file_object
    def incPos(self, blk_size):
        self.FILE_POS += blk_size
#    def getMidoFile(self):
#        import File
#        return File(file_data)
    def tell(self):
        return self.FILE_POS
    def read(self, buf_size):
        self.incPos(buf_size)
        data = self.STREAM.read(buf_size)
        return data

class TVVBlender():
    MOCK_BPY = None
    BPY = None
    PLAYER_NAME = "undefined"
    INSTRUMENT_NAME = "TBD"
    INSTRUMENT_CLASSNAME = "TBD"
    MIDI_FILE_NAME = "not selected"
    MIDI_FILE_TRACK_IDs = None
    def __init__(self):
        self.MOCK_BPY = os.environ.get("MOCK_BPY")
        if self.MOCK_BPY == 'True':
            from tvvbi.bpymock import bpy
            self.BPY = bpy
        else: # this only works from inside blender
            import bpy
            self.BPY = bpy
    def log(self, where, what):
        if DEBUG:
            print(where, what)
    def getFrameStart(self):
        return self.BPY.data.scenes[0].frame_start
    def setFrameStart(self, richie):
        self.BPY.data.scenes[0].frame_start = richie
    def getFrameEnd(self):
        return self.BPY.data.scenes[0].frame_end
    def setFrameEnd(self, richie):
        self.BPY.data.scenes[0].frame_end = richie
    def getFPS(self):
        return 30 # TBD
    def setFPS(self, richie):
        pass
    def getPlayerName(self):
        return self.PLAYER_NAME
    def setPlayerName(self, richie):
        self.PLAYER_NAME = richie
    def getInstrumentName(self):
        return self.INSTRUMENT_NAME
    def setInstrumentName(self, richie):
        self.INSTRUMENT_NAME = richie
    def getMidiFileName(self):
        return self.MIDI_FILE_NAME
    def setMidiFileName(self, richie):
        self.MIDI_FILE_NAME = richie
    def getMidiTrackList(self, midi_file):
        if midi_file == None:
            return None
        midi_file_obj = TVVMidoFile(midi_file)
        from mido import MidiFile
        midi = MidiFile(file=midi_file_obj)
        if None == midi:
            self.log( 'TVVBlender.getMIDITrackList()', ":Can't load MIDI file")
            return None
        trackList = None
        for i, miditrack in enumerate(midi.tracks):
            self.log( 'TVVBlender.getMIDITrackList():', "<i, miditrack>=<{},{}>".format(i,miditrack.name))
            if miditrack.name not in (None, "", " "):
                if None == trackList:
                    trackList = []
                trackList.append({"track_id": i, "track_name" : miditrack.name})
        return trackList
    def getMidiTrackIDs(self):
        return self.MIDI_FILE_TRACK_IDs
    def setMidiTrackIDs(self, richie):
        self.MIDI_FILE_TRACK_IDs = richie
    def getObjectList(self):
        return self.BPY.data.objects
    def removeObjectWithName(self, object_name):
        if None != object_name:
            objs = self.BPY.data.objects
            objs.remove(objs[object_name], True)
    def getCenterOfObject(self, o):
        vcos = [ o.matrix_world * v.co for v in o.data.vertices ]
        findCenter = lambda l: ( max(l) + min(l) ) / 2
        x,y,z  = [ [ v[i] for v in vcos ] for i in range(3) ]
        center = [ findCenter(axis) for axis in [x,y,z] ]
        return center
    def getBlenderVersion(self):
        return self.BPY.app.version
    def append(self, blend_file_path, obj_name):
        print("BI.append():<blend_file_path, obj_name><{},{}>".format(blend_file_path, obj_name))
        # append, set to true to keep the link to the original file
        link_flag = False
        # link all objects starting with 'Cube'
        with self.BPY.data.libraries.load(blend_file_path, link=link_flag) as (data_from, data_to):
            print("BI.append(): appending:<{}>".format(data_from))
            data_to.objects = [name for name in data_from.objects]
#            data_to.objects = [name for name in data_from.objects if name.startswith(obj_name)]
        #link object to current scene
        for obj in data_to.objects:
            if obj is not None:
                print("BI: linking:<{}>".format(obj))
                self.BPY.context.scene.objects.link(obj)
    def save(self, blend_file_path):
        print("BI.save():<blend_file_path><{}>".format(blend_file_path))
        self.BPY.ops.wm.save_as_mainfile(filepath=blend_file_path)
    def getInstrumentMap(self):
        return TVVAnimator().getInstrumentClasses()

    def getInstrumentClassName(self):
        return self.INSTRUMENT_CLASSNAME
    def setInstrumentClassName(self, instrument_class):
        self.INSTRUMENT_CLASSNAME = instrument_class
    def DEPRICATEgetInstrumentClassname(self, instrument_name):
        instrument_name_list = instrument_name.lower().split('_')
        test_instrument_name = ""
        for item in instrument_name_list:
            test_instrument_name += item
        print("BI.getInstrumentClassname():<test_instrument_name><{}>".format(test_instrument_name))
        for item in self.getInstrumentMap():
            test_item = item[0].lower()
            print("BI.getInstrumentClassname():<test_item><{}>".format(test_item))
            if test_item == test_instrument_name:
                return item[0]
        return None
    def getMonitorTrackIDs(self, instrument_class_name):
        icnl = instrument_class_name.lower()
        for item in self.getInstrumentMap():
            icl = item[0].lower()
            if icl == icnl:
                track_ind = item[2]
                ids = self.getMidiTrackIDs()
                if None == track_ind:
                    return ids[0]
                if isinstance(track_ind, list):
                    if track_ind.__len__() < 3:
                        return [ids[0], ids[1]]
                    else:
                        return ids
        return None
    def assemble(self):
        midi_file = "TLSwSC_Theme/Humanism.mid"
        playerName = self.getPlayerName()
        instrumentName = self.getInstrumentName()
        print("BI.assemble():<instrumentName><{}>".format(instrumentName))
        midiFileName = self.getMidiFileName()
        track_s = self.getMidiTrackIDs()
        from tvvanimator import TVVAnimator
        tvv = TVVAnimator()
        tvv.setFrameRate(self.getFPS())
        tvv.setCharacterName(playerName)
        tvv.setInstrumentName(instrumentName)
        icn = self.getInstrumentClassName()
        print("BI.assemble():<icn><{}>".format(icn))
        tvv.setInstrumentClassName(icn)
        tvv.setMIDIFileName(self.getMidiFileName())
        if None != track_s:
            tvv.setMonitorTrackId(track_s)
        #print("BI.assemble():<tracklist><{}>".format(tvv.getMIDITrackList()))
        tvv.animate()
    def terminate(self):
        self.BPY.ops.wm.quit_blender()
        
    