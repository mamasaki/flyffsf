import encodings, struct, time, sys, os.path, traceback
		
class Mesh(object):
        def __init__(self):
                self.reset()

	def reset(self):
                self.faces=[]
		self.verts=[]
                self.normals=[]
		self.uv=[]
		self.animated=0
		self.texname = ''
		self.xcount = 0
		self.xdata = 0
		self.xxcount = 0
		self.xxdata = 0
		self.vertbone = 0
		self.bones = 0
		self.ele1 = 0
		self.ele2 = 0
		self.itemkind = 0
		
        def pprint(self, s):
                if (1 == 2):
                        print s

	# makelist ((x,y,z),(x,y,z)) -> (x,y,z,x,y,z)
	def makelist3(self,liste):
                points = []
                for p in liste:
                        points.append(p[0])
                        points.append(p[1])
                        points.append(p[2])
                return points

	def makelist2(self,liste):
                points = []
                for p in liste:
                        points.append(p[0])
                        points.append(p[1])
                return points

	def flipuv(self):
		newuv=[]
		for i in self.uv:
			u=i[0]
			v=i[1]
			if (u > 1):
				u=i[0]-1
			if (v < 0):
				v=i[1]+1
			newuv.append((u,1-v))
		self.uv=newuv
		
	def normalize_vert(self, v):
                vx = 0
                vy = 0
                vz = 0
                _len = (v[0]**2 + v[1]**2 + v[2]**2)**0.5
                if (_len != 0):
                        vx = v[0] / _len
                        vy = v[1] / _len
                        vz = v[2] / _len
                #print vz
                return (vx,vy,vz)
        
        def normalize_tri(self, p1,p2,p3):
                Ax = p1[0]-p2[0]
                Ay = p1[1]-p2[1]
                Az = p1[2]-p2[2]

                Bx = p3[0]-p2[0]
                By = p3[1]-p2[1]
                Bz = p3[2]-p2[2]

                normalx = Ay*Bz - Az*By
                normaly = Az*Bx - Ax*Bz
                normalz = Ax*By - Ay*Bx

                return self.normalize_vert((normalx,-normaly,-normalz))

        #def filenametranslate(self, f):
        #        return (lambda x:"".join(map(dict(zip('abcdefghijklmnopqrstuvwxyz0123456789._ABCDEFGHIJKLMNOPQRSTUVWXYZ', map(''.join,zip(*(iter('ACAFAEA9A8ABAAA5A4A7A6A1A0A3A2BDBCBFBEB9B8BBBAB5B4B7FDFCFFFEF9F7FBFAF5F4E3928C8F8E89888B8A85848786818083829D9C9F9E99989B9A959497'),)*2)))).__getitem__,x)))(f).decode('hex')

        def filenametranslate(self, f):
                o = ''
                for i in xrange(len(f)):
                        o += chr(ord(f[i]) ^ 205)
                return o
                
        def loadO3d(self, f):
                
                try:
                        self.reset() # clear all variables of the instance
                        f=open(f,'rb')
                        fnamelen = ord(f.read(1))
                        filename = f.read(fnamelen) # read the filename
                        n = f.read(4) # version 0x14, 0x15, 0x16
                        self.pprint("version 0x15-16: "+str(n.encode('hex')))
                        version = struct.unpack('i',n)[0]
                        n = f.read(4) # 4x byte ??

                        ele1x = f.read(4) # element1 attach start point
                        ele1y = f.read(4)
                        ele1z = f.read(4)
                        ele1xend = f.read(4)
                        ele1yend = f.read(4)
                        ele1zend = f.read(4) # element1 attach end point
                        self.ele1 = [ele1x,ele1y,ele1z,ele1xend,ele1yend,ele1zend]
                        for x in xrange(len(self.ele1)):
                                self.ele1[x] = struct.unpack('f',self.ele1[x])[0]       
                        self.pprint(self.ele1)

                        
                        if (version == 22):
                                ele2x = f.read(4) # element2 attach start point
                                ele2y = f.read(4)
                                ele2z = f.read(4)
                                ele2xend = f.read(4)
                                ele2yend = f.read(4)
                                ele2zend = f.read(4) # element2 attach end point
                                self.ele2 = [ele2x,ele2y,ele2z,ele2xend,ele2yend,ele2zend]
                                for x in xrange(len(self.ele2)):
                                        self.ele2[x] = struct.unpack('f',self.ele2[x])[0]
                                
                        n = f.read(8) # 2x 0x00
                        n = f.read(16) # 16 chars of filename again
                        n = f.read(24) # bounding box?
                        n = f.read(4) # dword 0x3F
                        self.pprint("always 0x3F: "+str(n.encode('hex')))
                        n = f.read(4) # flag01
                        flag2 = struct.unpack('i',f.read(4))[0] # flag02
                        #self.pprint("flag2: "+str(flag2))
                        uknData2 = f.read(flag2*12) # struct with 3x float = 12bytes * flag2
                        meshtypeflag = f.read(4)
                        LODFlag = f.read(4)
                        Flag03 = f.read(4)
                        TotalMeshCount = f.read(4)
                        #print TotalMeshCount.decode('hex')
                        lodCount = struct.unpack("i",f.read(4))[0] # dword -> intval
                        self.pprint(str(lodCount)+" detail levels (aka meshes)")

                        for xi in xrange(1): #actually there are <lodCount> meshes, i only use LOD0 = best resolution
                                self.pprint("LOD"+str(xi))
                                #n = f.read(4) # dword
                                n = f.read(4) # dword, probably the bone indicator
                                hasBones = struct.unpack('i',n)[0]
                                self.pprint("has bones: "+n.encode('hex'))
                                if (hasBones == 1):
                                        self.animated = 1
                                else:
                                        self.animated = 0
                                uknblob = f.read(4)
                                #self.pprint(uknblob.encode('hex'))
                                uknCount3 = struct.unpack('i',uknblob)[0] # something related to bones
                                itemkind = f.read(uknCount3*4) # uknCount3 x dword
                                n = f.read(4) # dword
                                nTerm = f.read(4) # nTerminator = 0xFFFFFFFF
                                self.pprint("Terminator 0xFFFFFFFF: "+str(nTerm.encode('hex')))
                                
                                #transformation matrix
                                for i in xrange(16):
                                        n = f.read(4)
                                
                                #Bounding Box
                                n, = struct.unpack('f',f.read(4))
                                self.BBoxX = [n]
                                n, = struct.unpack('f',f.read(4))
                                self.BBoxY = [n]
                                n, = struct.unpack('f',f.read(4))
                                self.BBoxZ = [n]
                                n, = struct.unpack('f',f.read(4))
                                self.BBoxX.append(n)
                                n, = struct.unpack('f',f.read(4))
                                self.BBoxY.append(n)
                                n, = struct.unpack('f',f.read(4))
                                self.BBoxZ.append(n)

                                n = f.read(40) # always 0x00
                                
                                self.pprint(n.encode('hex'))
                                if (nTerm.encode('hex') == '06000000'): # If this is the case, it's robably a static CAP/HAT, those are tilted!
                                        n = f.read(4)

                                XCount = struct.unpack("i",f.read(4))[0]
                                self.pprint("Xcount: "+str(XCount))
                                VtCount = struct.unpack("i",f.read(4))[0]
                                self.pprint("Verts: "+str(VtCount))
                                FcCount = struct.unpack("i",f.read(4))[0]
                                self.pprint("Faces: "+str(FcCount))
                                FcSize = struct.unpack('i',f.read(4))[0]
                                self.pprint("Normals: "+str(FcSize))

                                xdata = []
                                
                                # XData -> Vert Shader?
                                for i in xrange(XCount):
                                        n = f.read(4)
                                        m = f.read(4)
                                        o = f.read(4)
                                        xdata.append((struct.unpack("f",n)[0],struct.unpack("f",m)[0]+.5,struct.unpack("f",o)[0]))
                                        #print struct.unpack('f',n),struct.unpack('f',m),struct.unpack('f',o)
                        
                                VertPool = []
                                Normals = []
                                UVmap = []
                                
                                boneDict =  {'dummy':[0,1]}
                                vertbone = {'dummy':1}
                                vertweight = {'dummy':1}
                                faceuvindex = {'dummy':1}

                                for i in xrange(VtCount):
                                        n = f.read(4)
                                        posX = struct.unpack("f",n)[0]
                                        n = f.read(4)
                                        posY = struct.unpack("f",n)[0]
                                        n = f.read(4)
                                        #print n.encode('hex')
                                        posZ = struct.unpack("f",n)[0]
                                        #print "face "+str(i+1)+" "+str(posX),str(posY),str(posZ)
                                        VertPool.append((posX,posY,posZ))
                                        if (hasBones == 1): 		  # no bones, no bone-info
                                                weight1 = f.read(4)
                                                weight2 = f.read(4)
                                                vertweight[i] = weight1.encode('hex')+weight2.encode('hex')
                                                bone1 = f.read(2)
                                                bone2 = f.read(2)
                                                c = bone1.encode('hex')+bone2.encode('hex')

                                                vertbone[i] = c
                                                
                                                if (c in boneDict):
                                                        crap = boneDict[c]
                                                        crap.append(i)
                                                        boneDict[c] = crap
                                                else:
                                                        tmps = []
                                                        tmps.append(i)
                                                        boneDict[c] = tmps
                                                #self.pprint('vert '+str(i)+' : '+bone1.encode('hex')+", "+bone2.encode('hex')+' weights: '+weight1.encode('hex')+' '+weight2.encode('hex'))


                                        NormalX = struct.unpack("f",f.read(4))[0]
                                        #print i, NormalX
                                        NormalY = struct.unpack("f",f.read(4))[0]
                                        NormalZ = struct.unpack("f",f.read(4))[0]
                                        Normals.append((NormalX,NormalY,NormalZ))
                                        UVu = struct.unpack("f",f.read(4))[0]
                                        UVv = struct.unpack("f",f.read(4))[0]
                                        UVmap.append((UVu,UVv))
                                        faceuvindex[i] = i
                                        #print i,posX, posY, posZ
                                del boneDict['dummy']
                                del vertbone['dummy']
                                del vertweight['dummy']
                                del faceuvindex['dummy']
                                #print sorted(boneDict.keys())
                                #print boneDict
                                #print vertbone

                                FacePool = []

                                for i in xrange(FcCount):
                                        id1 = ''
                                        id1 = f.read(2)
                                        id1 = struct.unpack('h',id1)[0]
                                        id2 = struct.unpack("h",f.read(2))[0]
                                        id3 = struct.unpack("h",f.read(2))[0]
                                        FacePool.append((id1,id2,id3))
                                #print FacePool
                                for i in xrange(VtCount):
                                        idx = struct.unpack("h",f.read(2))
                                        #print idx
                                n = f.read(4)
                                XXCount, =  struct.unpack("i",n) #same as XCount
                                self.xxdata = []
                                #self.pprint("XXCount: "+str(XXCount)+" "+n.encode('hex'))
                                #print XXCount
                                for i in xrange(XXCount):
                                        n = f.read(4)
                                        #self.pprint("XXData :"+n.encode('hex'))
                                        self.xxdata.append(n.encode('hex'))
                                #XXData = f.read(4*XXCount)
                                #print XXData.encode('hex')
                        
                                # materials

                                n = f.read(4)
                                MatCount = struct.unpack("i",f.read(4))[0]
                                if (MatCount == 0):
                                        MatCount = 1
                                self.pprint(str(MatCount)+" Materials")
				Texture=[]
                                for i in xrange(MatCount):
                                        colorRGBA = f.read(16) # -> void for now
                                        #print "Colors: "+colorRGBA.encode('hex')
                                        colorRGBA = f.read(16) # -> void for now
                                        #print "Colors: "+colorRGBA.encode('hex')
                                        colorRGBA = f.read(16) # -> void for now
                                        #print "Colors: "+colorRGBA.encode('hex')
                                        colorRGBA = f.read(16) # -> void for now
                                        #print "Colors: "+colorRGBA.encode('hex') 
                                        n = f.read(4)
                                        n = f.read(4)
                                        TexLeg = struct.unpack('i',n)[0]
                                        #print n.encode('hex')
                                        #print TexLeg
                                        Texture.append(f.read(TexLeg-1))                                     
                                        #print "Texture: "+Texture
				self.texname = Texture
				#print self.texname
                                matIDCount = struct.unpack("i",f.read(4))[0]
                                #print matIDCount
                                n = f.read(4)
                                n = f.read(4)
                                self.pprint("Textures Faces: "+str(struct.unpack('i',n)))
                                n = f.read(matIDCount*128)

                        f.close()
                        self.normals = Normals
                        self.verts = VertPool
                        self.faces = FacePool
			self.uv = UVmap
			self.vertbone = vertbone
			self.vertweight = vertweight
			self.faceuvindex = faceuvindex
			crap = {'d':1}
			for i in sorted(boneDict.keys()):
                                crap[i] = len(crap)-1
                        del crap['d']
			self.bones = crap
			self.xcount = XCount
			self.xdata = xdata
			self.xxcount = XXCount
			self.itemkind = itemkind

                except:
                        et, ev, tb = sys.exc_info()  
                        line_no =  "o3d.py, loadO3d Error Line # = " + str(traceback.tb_lineno(tb)) 
                        co = tb.tb_frame.f_code
                        print line_no, et, ev
                        print "An Error occured."
                        
        def loadObj(self, file):
                try:
                        self.reset()
                        parsestep=0
                        f=open(file,'rb')
                        n=f.readline()
                        sele = ''
                        VertPool=[]
                        FacePool=[]
                        FaceNormals=[]
                        Normals=[]
                        UVs=[]
                        UVindex=[]
                        FaceUVindex={'dummy':1}
                        ElePool=[]
                        EleFace=[]
                        while (n != ''):
                                if (n.split('#')[0] != ''):
                                        q = n.split(' ')
                                        t = q[0]
                                        if (len(q) > 1):
                                                sele = q[0].lower()+" "+q[1].lower().strip('\r\n')
                                        if (sele == 'g element'):
                                                parsestep = 1
                                                #print "element found"
                                        elif (q[0].lower() == "g" and q[1].lower().strip('\r\n') != "element"):
                                                if (parsestep == 1):
                                                        parsestep = 2
                                                else:
                                                        parsestep = 0
                                        if (parsestep != 1):
                                                if (t == 'v'):
                                                        VertPool.append((float('%f' % float(q[1])),float('%f' % float(q[2])),float('%f' % float(q[3].strip('\r\n')))))
                                                if (t == 'vt'):
                                                        UVs.append((float('%f' % float(q[1])),float('%f' % float(q[2].strip('\r\n')))))
                                                if (t == 'vn'):
                                                        Normals.append((float('%f' % float(q[1])),float('%f' % float(q[2])),float('%f' % float(q[3].strip('\r\n')))))
                                                if (t == 'f'):
                                                        # eg f 1/1/1 2/2/2 3/3/3
                                                        if (not parsestep):
                                                                f1 = int(q[1].split('/')[0])-1
                                                        else:
                                                                if (len(EleFace) == 1):
                                                                        f1 = int(q[1].split('/')[0])-1-3
                                                                else:
                                                                        f1 = int(q[1].split('/')[0])-1-5
                                                        f2 = int(q[2].split('/')[1])-1
                                                        f3 = int(q[3].strip('\r\n').split('/')[1])-1
                                                        #print q, f1,f2
                                                        FacePool.append((f1,f2,f3))
                                                        FaceUVindex[f1] = int(q[1].split('/')[1])-1
                                                        FaceUVindex[f2] = int(q[2].split('/')[1])-1
                                                        FaceUVindex[f3] = int(q[3].split('/')[1])-1
                                                        UVindex.append(int(q[1].split('/')[1])-1)
                                                        UVindex.append(int(q[2].split('/')[1])-1)
                                                        UVindex.append(int(q[3].strip('\r\n').split('/')[1])-1)
                                        else:
                                                if (t == 'v'):
                                                        ElePool.append((float('%f' % float(q[1])),float('%f' % float(q[2])),float('%f' % float(q[3].strip('\r\n')))))
                                                if (t == 'f'):
                                                        # eg f 1/1/1 2/2/2 3/3/3
                                                        f1 = int(q[1].split('/')[0])-1
                                                        f2 = int(q[2].split('/')[0])-1
                                                        f3 = int(q[3].strip('\r\n').split('/')[0])-1
                                                        
                                                        EleFace.append((f1,f2,f3))
                                                                                                
                                n = f.readline()
                        if (len(EleFace) > 1):
                                #print EleFace[1][0]-len(VertPool)
                                if (parsestep == 1):
                                        self.ele1 = [ElePool[EleFace[0][1]-len(VertPool)][0],ElePool[EleFace[0][1]-len(VertPool)][1],ElePool[EleFace[0][1]-len(VertPool)][2],ElePool[EleFace[0][2]-len(VertPool)][0],ElePool[EleFace[0][2]-len(VertPool)][1],ElePool[EleFace[0][2]-len(VertPool)][2]]
                                else:
                                        #print len(ElePool),EleFace[0][1]
                                        self.ele1 = [ElePool[EleFace[0][1]][0],ElePool[EleFace[0][1]][1],ElePool[EleFace[0][1]][2],ElePool[EleFace[0][2]][0],ElePool[EleFace[0][2]][1],ElePool[EleFace[0][2]][2]]
                                if (len(EleFace) == 2):
                                        if (parsestep == 1):                                                                                                             
                                                self.ele2 = [ElePool[EleFace[1][1]-len(VertPool)][0],ElePool[EleFace[1][1]-len(VertPool)][1],ElePool[EleFace[1][1]-len(VertPool)][2],ElePool[EleFace[1][2]-len(VertPool)][0],ElePool[EleFace[1][2]-len(VertPool)][1],ElePool[EleFace[1][2]-len(VertPool)][2]]
                                        else:
                                                self.ele2 = [ElePool[EleFace[1][1]][0],ElePool[EleFace[1][1]][1],ElePool[EleFace[1][1]][2],ElePool[EleFace[1][2]][0],ElePool[EleFace[1][2]][1],ElePool[EleFace[1][2]][2]]
                        del FaceUVindex['dummy']
                        f.close()
                        #print 'FaceUVindex',FaceUVindex
                        #print 'facepool',FacePool
                        
                        self.BBoxX = [s[0] for s in VertPool]
                        self.BBoxY = [s[1] for s in VertPool]
                        self.BBoxZ = [s[2] for s in VertPool]
                        #print min(BBoxX)
                        
                        self.pprint("> Faces: "+str(len(FacePool)))
                        self.pprint("> Verts: "+str(len(VertPool)))
                        # normalize mesh
                        x = 0
                        for i in FacePool:
                                FaceNormals.append(self.normalize_tri(VertPool[int(i[0])],VertPool[int(i[1])],VertPool[int(i[2])]))
                                x=x+1
                        self.pprint("done normalizing triangles")
                        for i in xrange(len(VertPool)):
                                tmpx = 0
                                tmpy = 0
                                tmpz = 0
                                count = 0
                                for x in xrange(len(FacePool)):
                                        if (FacePool[x][0] == i or FacePool[x][1] == i or FacePool[x][2] == i):
                                                tmpx = tmpx+FaceNormals[x][0]
                                                tmpy = tmpy+FaceNormals[x][1]
                                                tmpz = tmpz+FaceNormals[x][2]
                                                count=count+1
                                if (count > 0):
                                        tmpx = tmpx/count
                                        tmpy = tmpy/count
                                        tmpz = tmpz/count
                                else:
                                        tmpx = 1
                                        tmpy = 1
                                        tmpz = 1

                                if (len(Normals) <= i):
                                        Normals.append(self.normalize_vert((tmpx,tmpy,tmpz)))
                                else:
                                        Normals[i] = self.normalize_vert((tmpx,tmpy,tmpz))
                                #print Normals[i]
                        self.pprint("done computing normals")
                        self.normals = Normals
                        self.verts = VertPool
                        self.faces = FacePool
                        self.faceuvindex = FaceUVindex
			self.uv = UVs
			self.flipuv()
			self.xdata = list(set(VertPool))
			self.xcount = len(self.xdata)


                except:
                        et, ev, tb = sys.exc_info()  
                        line_no =  "o3d.py, loadObj Error Line # = " + str(traceback.tb_lineno(tb)) 
                        co = tb.tb_frame.f_code
                        print line_no, et, ev
                        print "An Error occured."

        def saveObj(self, file):
                try:
                        #print self.normals
                        fw=open(file,'w')
                        fw.write('# converter v3 by crosbow\n')
                        fw.write("g Mesh\n")
                        #print self.vertbone
                        for pos, i in enumerate(self.verts):
                                stromboli = "v "+str(i[0])+" "+str(i[1])+" "+str(i[2])+"\n"
                                fw.write(stromboli)
                                if (self.animated):
                                        fw.write("#b "+self.vertbone[pos]+"\n")
                        for i in self.uv:
                                u=i[0]
                                v=i[1]
                                if (u > 1):
                                        u=i[0]-1
                                if (v < 0):
                                        v=i[1]+1
                                stromboli = "vt "+str(u)+" "+str(1-v)+"\n"
                                fw.write(stromboli)
                        for i in self.normals:
                                stromboli = "vn "+str(i[0])+" "+str(i[1])+" "+str(i[2])+"\n"
                                fw.write(stromboli)
                        for i in self.faces:
                                #stromboli = "f "+str(i[0])+" "+str(i[1])+" "+str(i[2])+"\n"
                                stromboli = "f "+str(i[0]+1)+"/"+str(i[0]+1)+"/"+str(i[0]+1)+" "+str(i[1]+1)+"/"+str(i[1]+1)+"/"+str(i[1]+1)+" "+str(i[2]+1)+"/"+str(i[2]+1)+"/"+str(i[2]+1)+"\n"
                                fw.write(stromboli)
                        fw.write("g Element\nv 0 0 0\n")
                        fw.write("v "+str(self.ele1[0])+" "+str(self.ele1[1])+" "+str(self.ele1[2])+"\n")
                        fw.write("v "+str(self.ele1[3])+" "+str(self.ele1[4])+" "+str(self.ele1[5])+"\n")
                        if (self.ele2):
                                fw.write("v "+str(self.ele2[0])+" "+str(self.ele2[1])+" "+str(self.ele2[2])+"\n")
                                fw.write("v "+str(self.ele2[3])+" "+str(self.ele2[4])+" "+str(self.ele2[5])+"\n")
                        fw.write("f "+str(len(self.verts)+1)+" "+str(len(self.verts)+2)+" "+str(len(self.verts)+3)+"\n")
                        if (self.ele2):
                                fw.write("f "+str(len(self.verts)+1)+" "+str(len(self.verts)+4)+" "+str(len(self.verts)+5)+"\n")
                        fw.close()
                except:
                        et, ev, tb = sys.exc_info()  
                        line_no =  "o3d.py, saveObj Error Line # = " + str(traceback.tb_lineno(tb)) 
                        co = tb.tb_frame.f_code
                        print line_no, et, ev
                        print "An Error occured."

        def saveO3d(self, path, filen, texturename):
                try:
                        #print self.normals
                        fw=open(path,'wb')

                        # write filename 
                        fw.write(struct.pack('b',len(filen)))
                        uknCount1 = len(filen)
                        fw.write(self.filenametranslate(filen))

                        # write version?
                        if (self.ele2):
                                fw.write('16000000'.decode('hex')) # if we place 2 elemental glow lanes 0x16 else 0x15/0x14
                        else:
                                fw.write('14000000'.decode('hex'))
                                
                        fw.write('F794C0E0'.decode('hex')) # whats that?

                        # write elemental glow data
                        if (self.ele1 == 0):
                                self.ele1 = [0,0,0,0,0,0]
                        for x in self.ele1:
                                fw.write(struct.pack('f',x))
                        if (self.ele2):
                                for x in self.ele2:
                                        fw.write(struct.pack('f',x))
                           
                        fw.write('0000000000000000'.decode('hex')) # 2x \x00
                        
                        fw.write(self.filenametranslate(filen)[0:16].ljust(16, "\x00")) # filename[16]
                        fw.write('08B2EEBE89827AB9B3C84CBED58BEE3E0B8AC13F2768463E'.decode('hex')) # bounding box

                        fw.write('0000003F'.decode('hex')) # always \x3F

                        fw.write('00000000'.decode('hex')) # flag01
                        fw.write('00000000'.decode('hex')) # flag02

                        # fw.write('') flag02 * float X 3 -> use of this???

                        fw.write('00000000'.decode('hex')) # MeshTypeFlag
                        fw.write('00000000'.decode('hex')) # LODFlag
                        fw.write('00000000'.decode('hex')) # Flag03?
                        fw.write('01000000'.decode('hex')) # TotalMeshCount
                        fw.write('01000000'.decode('hex')) # MeshCount

                        for xi in xrange(1): #actually there are <lodCount> meshes, i only use LOD0 = best resolution

                                # Has bones
                                if (self.animated):
                                        fw.write(struct.pack('i',1)) 
                                else:
                                        fw.write(struct.pack('i',0))

                                # Meshtype, this defines if its boots, chest balbal, dunno how its set up
                                if (self.itemkind):
                                        fw.write(struct.pack('i',len(self.itemkind)/4)) #len
                                        fw.write(self.itemkind)
                                else:
                                        fw.write(struct.pack('i',0))

                                # Effect unkown, for armors around 0x20
                                fw.write(struct.pack('i',0))

                                # The terminator
                                fw.write('FFFFFFFF'.decode('hex'))
                                
                                # Transformation Matrix testing values
                                fw.write(struct.pack('f',float(1)))
                                fw.write(struct.pack('f',float(0)))
                                fw.write(struct.pack('f',float(0)))
                                fw.write(struct.pack('f',float(0)))

                                fw.write(struct.pack('f',float(0)))
                                fw.write(struct.pack('f',float(1)))
                                fw.write(struct.pack('f',float(0)))
                                fw.write(struct.pack('f',float(0)))

                                fw.write(struct.pack('f',float(0)))
                                fw.write(struct.pack('f',float(0)))
                                fw.write(struct.pack('f',float(1)))
                                fw.write(struct.pack('f',float(0)))

                                fw.write(struct.pack('f',float(0)))
                                fw.write(struct.pack('f',float(3.9999996204187482e-08)))
                                fw.write(struct.pack('f',float(5.9999997858994902e-08)))
                                fw.write(struct.pack('f',float(1)))

                                # Bounding Box
                                fw.write(struct.pack('f',min(self.BBoxX)))
                                fw.write(struct.pack('f',min(self.BBoxY)))
                                fw.write(struct.pack('f',min(self.BBoxZ)))
                                fw.write(struct.pack('f',max(self.BBoxX)))
                                fw.write(struct.pack('f',max(self.BBoxY)))
                                fw.write(struct.pack('f',max(self.BBoxZ)))

                                fw.write(('00'*40).decode('hex'))

                                # Vertcount etc
                                fw.write(struct.pack("i",self.xcount)) # whats XData? It looks like the other verts of the mesh. We only give it 3 Vert for test

                                fw.write(struct.pack('i',len(self.verts))) # write our new vert count
                                
                                fw.write(struct.pack('i',len(self.faces)))

                                fw.write(struct.pack('i',len(self.faces)*3))

                                # XData
                                for i in xrange(self.xcount):

                                        fw.write(struct.pack('f',self.xdata[i][0]))		
                                        fw.write(struct.pack('f',self.xdata[i][1]))
                                        fw.write(struct.pack('f',self.xdata[i][2]))

                                #print self.faceuvindex
                                #print self.faces
                                
                                for i in xrange(len(self.verts)):

                                        fw.write(struct.pack('f',float(self.verts[i][0])))

                                        fw.write(struct.pack('f',float(self.verts[i][1])))
                                
                                        fw.write(struct.pack('f',float(self.verts[i][2])))
                                        
                                        if (self.animated):
                                                #fw.write(self.vertweight[i].decode('hex')) #weight1
                                                #print self.vertweight[i]
                                                fw.write('0000803f00000000'.decode('hex')) #weight2
                                                fw.write(self.vertbone[i].decode('hex')) #bone1
                                                #fw.write('00000000'.decode('hex')) #bone2
 

                                        # if we lack normals, fill them up. actually unneccesary since import OBJ generates all Normals -> to be removed
                                        if (i >= len(self.normals)):
                                                self.normals.append((0.5,0.5,0.5))

                                        # Normals
                                        fw.write(struct.pack('f',float(self.normals[i][0])))
                                        fw.write(struct.pack('f',float(self.normals[i][1])))
                                        fw.write(struct.pack('f',float(self.normals[i][2])))

                                        # UV
                                        u = self.uv[self.faceuvindex[i]][0]
                                        v = self.uv[self.faceuvindex[i]][1]
                                        """if (u > 1):
                                                u=float(UVs[i][0])-1
                                        if (v < 0):
                                                v=float(UVs[i][1])+1"""
                                        fw.write(struct.pack('f',float(u)))
                                        fw.write(struct.pack('f',float(float(v))))

                                # Faces
                                
                                for i in xrange(len(self.faces)):
                                        id1 = ''

                                        fw.write(struct.pack('h',int(self.faces[i][0])))

                                        fw.write(struct.pack('h',int(self.faces[i][1])))

                                        fw.write(struct.pack('h',int(self.faces[i][2])))

                                # something xD forgot what it is..
                                for i in xrange(len(self.verts)):
                                        fw.write(struct.pack('h',1))

                                # XXData
                                if (self.animated):
                                        fw.write(struct.pack('i',self.xxcount))
                                        #print self.xxdata
                                        for i in xrange(self.xxcount):

                                                fw.write('00000000'.decode('hex')) # <-- whats it good for? maybe similar to boneweight
                                                #fw.write(self.xxdata[i].decode('hex'))
                                else:
                                        fw.write(struct.pack('i',0))
                        
                                # materials

                                fw.write(struct.pack('i',1))
                                # write number of materials
                                fw.write(struct.pack('i',0)) # write 0 materials (which is treated like 1)
                                MatCount = 1
                                #pprint(str(MatCount)+" Materials")
                                for i in xrange(MatCount):
                                        # write colors
                                        fw.write('0000803F0000803F0000803F000000000000803F0000803F0000803F000000006666663F6666663F6666663F0000000000000000000000000000000000000000'.decode('hex'))
                                        fw.write(struct.pack('i',0))
                                        # write texture name
                                        texlen = len(texturename)+1
                                        fw.write(struct.pack('i',int(texlen))) #length of filename
                                        if (texturename != ""):
                                                Texture = texturename+"00".decode('hex')
                                        fw.write(Texture)

                                fw.write(struct.pack('i',1))
                                fw.write(struct.pack('i',0))
                                fw.write(struct.pack('i',len(self.faces)))
                                fw.write('0000000006000000FF0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'.decode('hex'))

                        fw.close()

                except:
                        et, ev, tb = sys.exc_info()  
                        line_no =  "o3d.py, saveO3d Error Line # = " + str(traceback.tb_lineno(tb)) 
                        co = tb.tb_frame.f_code
                        print line_no, et, ev
                        print "An Error occured."

        def renameO3d(self, filen, new, keep):
                f=open(filen,'rb')
                fn=open(new,'wb')
                fn.write(struct.pack('b',len(os.path.basename(new))))
                fn.write(self.filenametranslate(os.path.basename(new)))
                n = f.read(1)
                n = f.read(struct.unpack('b',n)[0])
                version = f.read(4)
                fn.write(version)
                fn.write(f.read(28))                
                if (struct.unpack('i',version)[0] == 22):
                        fn.write(f.read(24))                         
                fn.write(f.read(8))
                n = f.read(16)
                fn.write(self.filenametranslate(os.path.basename(new))[0:16])
                fn.write(f.read())
                f.close()
                fn.close()
                if (keep == False):
                        os.remove(filen)
                
                        
                
