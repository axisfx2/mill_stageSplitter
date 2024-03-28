import c4d

class stageSplitter():
    def __init__(self, doc):
        
        self.doc = doc
        self.stage = doc.GetActiveObject()
        
        self.fps = doc.GetFps()
        
        if not self.stage or self.stage.GetType() != 5136:
            c4d.gui.MessageDialog('ERROR: Please select a stage')
            return
        
        camera_track_id = c4d.DescID(c4d.DescLevel(c4d.STAGEOBJECT_CLINK))
        camera_track = self.stage.FindCTrack(camera_track_id)
        
        if not camera_track:
            c4d.gui.MessageDialog('ERROR: Please add keyframes to the camera track')
            return

        self.doc.StartUndo()

        if self.getAllRenderData() or self.getAllTakeData():
            if c4d.gui.QuestionDialog('Delete All Takes and Render Settings?'):
                self.deleteAllRenderData()
                self.deleteAllTakes()

        self.dataListFromKeyframes(camera_track)
        self.createRenderData()
        self.createTakeData()
        
        self.doc.EndUndo()

        c4d.gui.MessageDialog(self.prettyStats())

    def prettyStats(self):
        n_cameras = len(self.camera_dict)
        n_takes = len(self.data_list)

        if n_cameras == 1:
            camera_plural = ''
        else:
            camera_plural = 's'

        if n_takes == 1:
            take_plural = ''
        else:
            take_plural = 's'

        stats = 'Successfully Generated {} Take{} from {} Camera{}'.format(
            n_takes,
            take_plural,
            n_cameras,
            camera_plural
        )

        return stats

    def getAllRenderData(self):
        rd = self.doc.GetFirstRenderData()
        rds = []
        
        while rd:
            rds.append(rd)
            rd = rd.GetNext()

        return rds
        
    def deleteAllRenderData(self):
        rds = self.getAllRenderData()
            
        for rd in rds[1:]:
            rd.Remove()

        c4d.EventAdd()
    
    def getAllTakeData(self):
        src_take_data = self.doc.GetTakeData()
        main_take = src_take_data.GetMainTake()
        td = main_take.GetDown()

        tds = []
        
        while td:
            tds.append(td)
            td = td.GetNext()

        return tds

    def deleteAllTakes(self):
        tds = self.getAllTakeData()
            
        for td in tds:
            td.Remove()
                
        c4d.EventAdd()

    def dataListFromKeyframes(self, camera_track):
        alphabet = 'abcdefghijklmnopqrstuvwxyz'

        camera_curve = camera_track.GetCurve()

        max_time = self.doc.GetMaxTime()
        
        # iterate over keyframes
        self.data_list = []
        self.camera_dict = {}

        keyframe_count = camera_curve.GetKeyCount()

        for k in range(keyframe_count):
            key = camera_curve.GetKey(k)
            time = key.GetTime()
            start_time = time#.GetFrame(fps)
            
            data = {}
            
            data['Frame Range'] = [start_time]
            
            if k > 0:
                end_time = start_time - c4d.BaseTime(1, self.fps)
                self.data_list[-1]['Frame Range'].append(end_time)
                
            if k == keyframe_count-1:
                data['Frame Range'].append(max_time)
            
            camera = key.GetGeData()
            
            camera_name = camera.GetName()
            
            if camera_name not in self.camera_dict:
                self.camera_dict[camera_name] = -1
            self.camera_dict[camera_name] += 1
            
            camera_letter = alphabet[self.camera_dict[camera_name]]
            
            take_name = camera_name
            take_name += '_{}'.format(camera_letter.upper())
            
            data['Take Name'] = take_name
            data['Camera'] = camera
            
            self.data_list.append(data)
            
        #[print(d) for d in self.data_list]
        #return
        #self.data_list.reverse()
        
    def createRenderData(self):
        src_render_data = self.doc.GetFirstRenderData()
        
        for data_dict in self.data_list:
            render_data: c4d.documents.RenderData = src_render_data.GetClone(c4d.COPYFLAGS_0)
            #data = doc.InsertRenderDataLast(clone)
            self.doc.InsertRenderDataLast(render_data)
            
            tstart, tend = data_dict['Frame Range']
            
            render_data.SetName(data_dict['Take Name'])
            render_data[c4d.RDATA_FRAMESEQUENCE] = 0
            render_data[c4d.RDATA_FRAMEFROM] = tstart
            render_data[c4d.RDATA_FRAMETO] = tend
            
            data_dict['Render Data'] = render_data

        c4d.EventAdd()
            
    def createTakeData(self):
        # create takes
        src_take_data = self.doc.GetTakeData()
        main_take = src_take_data.GetMainTake()
        child_take = main_take.GetDown()
        
        for data_dict in reversed(self.data_list):
            take_data = src_take_data.AddTake(
                '', main_take, child_take)
            
            take_data.SetName(data_dict['Take Name'])
                
            take_data.SetCamera(src_take_data, data_dict['Camera'])
            take_data.SetRenderData(src_take_data, data_dict['Render Data'])
            
            data_dict['Take Data'] = take_data
            #take_data.SetName(data_dict['Take Name'])

        c4d.EventAdd()

class CommandData(c4d.plugins.CommandData):
    def Execute(self, doc):
        stageSplitter(doc)
        return True

def main():
    # iconMTX = c4d.bitmaps.BaseBitmap()
    # iconMTX.InitWith(os.path.join(os.path.dirname(__file__), "res", "stageSplitter.png"))
    iconMTX = None
    # Register Plugin
    c4d.plugins.RegisterCommandPlugin(
        1062995, 
        'Stage Splitter', 
        0, 
        iconMTX,
        'Split stage object into takes and render settings per each keyframe', 
        CommandData()
    )

if __name__ == '__main__':
    main()