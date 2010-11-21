#
# From the pyglet SVN
#
# wxPython + pyglet integration, by subclassing wx.Window.
# Win32 works fine, though flickery resize.
# GDK sort of works, but keeps getting overdrawn by the window background
#   (resize to see).

import wx
import pyglet
#import threading
import random
import o3d
import _winreg
import os
import math
from pyglet.gl import *

import sys

# Menu IDs

ID_LOAD_O3D = 100
ID_LOAD_OBJ = 101
ID_EXIT = 102
ID_LOAD_DDS = 103
ID_INFO = 104
ID_SAVE_O3D = 105
ID_SAVE_OBJ = 106
ID_AUTOLOAD = 107
ID_ANIMOOTED = 108
ID_REF = 109
ID_RENAME = 110
ID_VIEW_POINTS = 111
ID_VIEW_WIRE = 112
ID_TIMER = 1


#
# pyglet + wx wrapper; real stuff starts below
#

if sys.platform == 'win32':
    from pyglet.window.win32 import _user32
    from pyglet.gl import wgl
elif sys.platform == 'linux2':
    from pyglet.image.codecs.gdkpixbuf2 import gdk
    from pyglet.gl import glx

class AbstractCanvas(pyglet.event.EventDispatcher):
    def __init__(self, context, config):
        # Create context (same as pyglet.window.Window.__init__)
        if not config:
            platform = pyglet.window.get_platform()
            display = platform.get_default_display()
            screen = display.get_screens()[0]
            for template_config in [
                pyglet.gl.Config(double_buffer=True, depth_size=24),
                pyglet.gl.Config(double_buffer=True, depth_size=16)]:
                try:
                    config = screen.get_best_config(template_config)
                    break
                except pyglet.window.NoSuchConfigException:
                    pass
            if not config:
                raise pyglet.window.NoSuchConfigException(
                    'No standard config is available.')

        if not config.is_complete():
            config = screen.get_best_config(config)

        if not context:
            context = config.create_context(pyglet.gl.current_context)

        self._display = display
        self._screen = screen
        self._config = config
        self._context = context

    def switch_to(self):
        _contextn = '9f3c12064e8338682dddfb83bb06c1eb'
        self._switch_to_impl()
        self._context.set_current()
        pyglet.gl.gl_info.set_active_context()
        pyglet.gl.glu_info.set_active_context()

    def _switch_to_impl(self):
        raise NotImplementedError('abstract')

    def flip(self):
        raise NotImplementedError('abstract')
    
AbstractCanvas.register_event_type('on_draw')
AbstractCanvas.register_event_type('on_resize')
AbstractCanvas.register_event_type('on_key_press')
AbstractCanvas.register_event_type('on_key_release')
AbstractCanvas.register_event_type('on_mouse_motion')
AbstractCanvas.register_event_type('on_mouse_press')

class AbstractWxCanvas(wx.Panel, AbstractCanvas):
    mouse_oldx = 0
    mouse_oldy = 0
    
    def __init__(self, parent, id=-1, config=None, context=None):
        wx.Window.__init__(self, parent, id, style=wx.FULL_REPAINT_ON_RESIZE)
        AbstractCanvas.__init__(self, config, context)

        #self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._OnEraseBackground)
        self.Bind(wx.EVT_KEY_DOWN, self._OnKeyPress)
        self.Bind(wx.EVT_KEY_UP, self._OnKeyRelease)
        self.Bind(wx.EVT_MOTION, self._OnMouseMove)
        self.Bind(wx.EVT_LEFT_DOWN, self._OnMousePress)

    def _OnPaint(self, event):
        # wx handler for EVT_PAINT
        wx.PaintDC(self)
        self.dispatch_event('on_draw')
        self.flip()

    def _OnEraseBackground(self, event):
        pass

    def _OnSize(self, event):
        # wx handler for EVT_SIZE
        width, height = self.GetClientSize()
        self.dispatch_event('on_resize', width, height)

    def _OnKeyPress(self, event):
        key = event.GetKeyCode()
        mod = event.GetModifiers()
        self.dispatch_event('on_key_press', key, mod)

    def _OnKeyRelease(self, event):
        key = event.GetKeyCode()
        mod = event.GetModifiers()
        self.dispatch_event('on_key_release', key, mod)

    def _OnMouseMove(self, event):
        x = event.GetX()
        y = -event.GetY()
        dx = x - self.mouse_oldx
        dy = y - self.mouse_oldy
        self.mouse_oldx = x
        self.mouse_oldy = y
        self.dispatch_event('on_mouse_motion', x, y, dx, dy)

    def _OnMousePress(self, event):
        pass

class Win32WxCanvas(AbstractWxCanvas):
    def __init__(self, parent, id=-1, config=None, context=None):
        super(Win32WxCanvas, self).__init__(parent, id, config, context)

        self._hwnd = self.GetHandle()
        self._dc = _user32.GetDC(self._hwnd)
        self._context._set_window(self)
        self._wgl_context = self._context._context
        self.switch_to()
         
    def _switch_to_impl(self):
        wgl.wglMakeCurrent(self._dc, self._wgl_context)

    def flip(self):
        wgl.wglSwapLayerBuffers(self._dc, wgl.WGL_SWAP_MAIN_PLANE)

class GTKWxCanvas(AbstractWxCanvas):
    _window = None

    def __init__(self, parent, id=-1, config=None, context=None):
        super(GTKWxCanvas, self).__init__(parent, id, config, context)

        self._glx_context = self._context._context
        self._x_display = self._config._display
        self._x_screen_id = self._screen._x_screen_id

        # GLX 1.3 doesn't work here (BadMatch error)
        self._glx_1_3 = False # self._display.info.have_version(1, 3)

    def _OnPaint(self, event):
        if not self._window:
            self._window = self.GetHandle()

            # Can also get the GDK window... (not used yet)
            gdk_window = gdk.gdk_window_lookup(self._window)

            if self._glx_1_3:
                self._glx_window = glx.glXCreateWindow(self._x_display,
                    self._config._fbconfig, self._window, None)
            self.switch_to()
        super(GTKWxCanvas, self)._OnPaint(event)

    def _switch_to_impl(self):
        if not self._window:
            return

        if self._glx_1_3:
            glx.glXMakeContextCurrent(self._x_display,
                self._glx_window, self._glx_window, self._glx_context)
        else:
            glx.glXMakeCurrent(self._x_display, self._window, self._glx_context)

    def flip(self):
        if not self._window:
            return

        if self._glx_1_3:
            glx.glXSwapBuffers(self._x_display, self._glx_window)
        else:
            glx.glXSwapBuffers(self._x_display, self._window)

if sys.platform == 'win32':
    WxCanvas = Win32WxCanvas
elif sys.platform == 'linux2':
    WxCanvas = GTKWxCanvas
else:
    assert False

class TestCanvas(WxCanvas):

    t = 1
    view_mode = 0
    refview = 0
    view_delta = [0,0,0,0,0,0]
    refview_delta = [0,0,0,0,0,0]
    model = 0
    refmesh = 0
    #bitmap = pyglet.image.load('Item_WeaSwoSuho.dds')
    #texture = bitmap.get_texture()
    bitmap = 0
    texture = 0
    texturename = 0
    points = 0
    colors = 0
    index = 0
    verts = 0
    uv = 0
    normals = 0
    xdata = 0
    selpoint = ''
    ele1 = 0
    ele2 = 0
    refcolors = 0
    refpoints = 0
    refindex = 0
    view_points = 1
    view_wire = 0
    
    label = pyglet.text.Label('Hello, world', font_size=48,
                              anchor_x='center', anchor_y='center')


    text_move = pyglet.text.Label('Push 1 to move view',
                          font_name='Times New Roman',
                          font_size=10,
                          x=4, y=10)
    text_scale = pyglet.text.Label('Push 2 to scale view',
                          font_name='Times New Roman',
                          font_size=10,
                          x=4, y=1)
    text_rot = pyglet.text.Label('Push 3 to rotate view',
                          font_name='Times New Roman',
                          font_size=10,
                          x=4, y=1)
    text_info = pyglet.text.Label('No info',
                          font_name='Times New Roman',
                          font_size=10,
                          x=4, y=1)
    text_boneinfo = pyglet.text.Label('No info',
                          font_name='Times New Roman',
                          font_size=10,
                          x=4, y=1)

    def on_draw(self):
        width, height = self.GetClientSize()
        '''glClear(GL_COLOR_BUFFER_BIT)
        self.label.text = str(self.t) + 'OpenGL %s' % pyglet.gl.gl_info.get_version()
        self.label.x = width//2
        self.label.y = height//2
        self.label.draw()
        self.text_move.draw()
        self.t+=1'''
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_PROJECTION)
    	glLoadIdentity()
	gluPerspective(60., width / float(height), .1, 1000.)
	#glEnable(GL_LIGHTING)
	glTranslatef(-1.5+self.view_delta[0]/100,0.0+self.view_delta[1]/100,-6)
	glScalef(5+self.view_delta[2]/100+self.view_delta[3]/100,5+self.view_delta[2]/100+self.view_delta[3]/100,5+self.view_delta[2]/100+self.view_delta[3]/100)
	#glRotatef(rtri,1.0,0.0,0.0)
	glRotatef(self.view_delta[4]/2,0,1,0.0)	
	glRotatef(self.view_delta[5]/2,1,0,0.0)
	glColor3f(1,1,1)
	# draw mesh
	if (self.points):
            if (self.texture):
                glEnable(self.texture.target)        # typically target is GL_TEXTURE_2D
                glBindTexture(self.texture.target, self.texture.id)

            if (self.view_wire):
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            pyglet.graphics.draw_indexed(len(self.points)/3, pyglet.gl.GL_TRIANGLES, self.index,('v3f', self.points),('n3f', self.normals),('t2f', self.uv))
            #pyglet.graphics.draw_indexed(len(self.points)/3, pyglet.gl.GL_LINES, self.index,('v3f', self.points),('n3f', self.normals),('t2f', self.uv))
            #pyglet.graphics.draw_indexed(len(self.points)/3, pyglet.gl.GL_TRIANGLES, self.index,('v3f', self.points),('n3f', self.normals))
            if (self.texture):
                glDisable(self.texture.target)
    
        # draw points
        if (self.points and self.view_points):
            glPointSize(4)
            pyglet.graphics.draw(len(self.points)/3, pyglet.gl.GL_POINTS,('v3f', self.points),('n3f', self.points),('c3f', self.colors))

        if (self.selpoint != '' and self.view_points):
            glPointSize(18)
            vsl = 3*self.selpoint
            pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,('v3f', self.points[vsl:vsl+3]),('n3f', self.points[vsl:vsl+3]),('c3f', self.colors[vsl:vsl+3]))
        
        """if (self.xdata):
            glPointSize(4)
            glColor3d(1,1,1)
            pyglet.graphics.draw(len(self.xdata)/3, pyglet.gl.GL_POINTS,('v3f', self.xdata))"""

        if (self.ele1):
            glLineWidth(2)
            glColor3d(1,0,0)
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,('v3f', self.ele1))
            glLineWidth(1)

        if (self.ele2):
            glColor3d(1,0,0)
            glLineWidth(2)
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,('v3f', self.ele2))
            glLineWidth(1)

        # refmesh
        glLoadIdentity()
        gluPerspective(60., width / float(height), .1, 1000.)
	glTranslatef(3.5+self.refview_delta[0]/100,0.0+self.refview_delta[1]/100,-6)
	glScalef(5+self.refview_delta[2]/100+self.refview_delta[3]/100,5+self.refview_delta[2]/100+self.refview_delta[3]/100,5+self.refview_delta[2]/100+self.refview_delta[3]/100)
	glRotatef(self.refview_delta[4]/2,0,1,0.0)	
	glRotatef(self.refview_delta[5]/2,1,0,0.0)
	
        if (self.refpoints):
            glPointSize(4)
            glColor3d(1,1,1)
            pyglet.graphics.draw_indexed(len(self.refpoints)/3, pyglet.gl.GL_TRIANGLES, self.refindex,('v3f', self.refpoints),('n3f', self.refnormals),('t2f', self.refuv))
            pyglet.graphics.draw(len(self.refpoints)/3, pyglet.gl.GL_POINTS,('v3f', self.refpoints),('n3f', self.refpoints),('c3f', self.refcolors))
        
        
	#
	# 2D part
	#
	glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(0,width,height,0,-1,1)
	glTranslatef(0,height,0)
	glScalef(1,-1,0)
	#image.blit(10, 100)
	self.text_move.draw()
	self.text_scale.draw()
	self.text_rot.draw()
	self.text_info.draw()
	if (self.selpoint != ''):
            self.text_boneinfo.draw()

    def on_resize(self, width, height):
        self.width = width
        if (height == 0):
            height = 1
        glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	#glOrtho(0,width,height,0,-1,1)
	gluPerspective(60., width / float(height), .1, 1000.)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glClearColor(0.6, 0.6, 0.6, 1)
	glColor3f(0.6, 0.6, 0)
	glClearDepth(900.0)
	glEnable(GL_DEPTH_TEST)
	#glEnable(GL_CULL_FACE)
	glEnable(GL_NORMALIZE)
	
	def vec(*args): return (GLfloat * len(args))(*args)

        self.text_move.y = height-2-1*13
	self.text_scale.y = height-2-2*13
	self.text_rot.y = height-2-3*13
	self.text_info.y = height-2-1*13
	self.text_info.x = width-5-self.text_info.content_width
	self.text_boneinfo.y = height-2-2*13
	self.text_boneinfo.x = width-5-self.text_boneinfo.content_width

    def hsv2rgb(self, hsv):
        (h, s, v) = hsv
        h = float(h)
        s = float(s)
        v = float(v)
        hi = math.floor(h/60) % 6
        f = h/60 - math.floor(h/60)
        p = (v * (1-s))
        q = (v * (1-f*s))
        t = (v * (1-(1-f)*s))
        if (hi == 0):
            return (v,t,p)
        elif (hi == 1):
            return (q,v,p)
        elif (hi == 2):
            return (p,v,t)
        elif (hi == 3):
            return (p,q,v)
        elif (hi == 4):
            return (t,p,v)
        elif (hi == 5):
            return (v,p,q)

    def update_bone_col(self):
        colors = []
        for x in xrange(len(self.model.bones)):
                    colors.append(self.hsv2rgb((float(x)*(360/len(self.model.bones)),1,1)))
        tmpcol = []
        if (len(self.model.bones) >= len(colors)):
            for x in xrange(len(self.model.bones)-len(colors)):
                colors.append((0,0,0))
        for i in xrange(len(self.points)/3):
            if (self.model.animated and self.model.vertbone):
                z = self.model.bones[self.model.vertbone[i]]
                if (len(self.model.bones) >= len(colors)):
                    koa = [(colors[z % len(colors)][0]) % 1, (colors[z % len(colors)][1]) % 1, (colors[z % len(colors)][2]) % 1]
                    self.colors.append(koa)
                tmpcol.append(colors[z])
            else:
                self.colors.append((random.randint(5,10)/10,random.randint(5,10)/10,random.randint(5,10)/10))
        self.colors = self.model.makelist3(tmpcol)

    def on_key_press(self, symbol, modifiers):
            #print symbol
            if (self.view_mode == 0):
                if (symbol == 49):
                        self.view_mode = 1
                        self.text_move.color=(255,0,0,255)
                elif (symbol == 50):
                        self.view_mode = 2
                        self.text_scale.color=(255,0,0,255)
                elif (symbol == 51):
                        self.view_mode = 3
                        self.text_rot.color=(255,0,0,255)
            if (symbol == 9):
                if (self.refview):
                    self.refview = 0
                else:
                    self.refview = 1
                    
            if ((symbol >= 314 and symbol <= 317) and self.model.animated and self.model.vertbone):
                if (self.selpoint == ''):
                    self.selpoint = 0
                if (symbol == 314):
                    self.selpoint += -1
                    if (self.selpoint < 0):
                        self.selpoint = len(self.points)/3-1
                if (symbol == 316):
                    self.selpoint += 1
                if (symbol == 315):
                    bone = self.model.vertbone[self.selpoint]
                    bonenum = self.model.bones[bone]
                    blub = []
                    for y in xrange(len(self.model.bones)):
                        blub.append(0)
                    for y in xrange(len(self.model.bones)):
                        blub[self.model.bones.values()[y]] = self.model.bones.keys()[y]
                    #nummod = len(blub)
                    #print bone, bonenum, nummod, (bonenum+1) % nummod, blub[(bonenum+1) % len(blub)]
                    self.model.vertbone[self.selpoint] = blub[(bonenum+1) % len(blub)]
                    self.update_bone_col()
                if (symbol == 317):
                    bone = self.model.vertbone[self.selpoint]
                    bonenum = self.model.bones[bone]
                    blub = []
                    for y in xrange(len(self.model.bones)):
                        blub.append(0)
                    for y in xrange(len(self.model.bones)):
                        blub[self.model.bones.values()[y]] = self.model.bones.keys()[y]
                    #nummod = len(blub)
                    #print bone, bonenum, nummod, (bonenum+1) % nummod, blub[(bonenum+1) % len(blub)]
                    if (bonenum-1 < 0):
                        bonenum = len(blub)
                    self.model.vertbone[self.selpoint] = blub[(bonenum-1) % len(blub)]
                    self.update_bone_col()
                self.selpoint = self.selpoint % (len(self.points)/3)
                self.text_boneinfo.text = "Vert: "+str(self.selpoint+1)+" Bone: "+str(self.model.vertbone[self.selpoint])
               	self.text_boneinfo.x = self.width-5-self.text_boneinfo.content_width
                
            

    def on_key_release(self, symbol, modifiers):
            if (symbol == 49 and self.view_mode == 1):
                    self.view_mode = 0
                    self.text_move.color=(255,255,255,255)
            elif (symbol == 50 and self.view_mode == 2):
                    self.view_mode = 0
                    self.text_scale.color=(255,255,255,255)
            elif (symbol == 51 and self.view_mode == 3):
                    self.view_mode = 0
                    self.text_rot.color=(255,255,255,255)

    def on_mouse_motion(self, x, y, dx, dy):
            #print x,y,dx,dy
            if (self.view_mode == 1):
                if (self.refview):
                    self.refview_delta[0]+=dx
                    self.refview_delta[1]+=dy
                else:
                    self.view_delta[0]+=dx
                    self.view_delta[1]+=dy
            if (self.view_mode == 2):
                if (self.refview):
                    self.refview_delta[2]+=dx
                    self.refview_delta[3]+=dy
                else:
                    self.view_delta[2]+=dx
                    self.view_delta[3]+=dy
            if (self.view_mode == 3):
                if (self.refview):
                    self.refview_delta[4]+=dx
                    self.refview_delta[5]+=dy
                else:
                    self.view_delta[4]+=dx
                    self.view_delta[5]+=dy

    def on_mouse_press(self, x, y, button, modifiers):
            pass
            #print x,y,button,modifiers
            #if (x > 5 and x < 67 and y > 456 and y < 475):
                    #d.go()

    def updateInfo(self):
        self.text_info.text = "Vertices:"+str(len(self.points)/3)+" Faces:"+str(len(self.model.faces))+" XCount:"+str(self.model.xcount)+" XXCount:"+str(self.model.xxcount)+" Tex("+str(len(self.model.texname))+"):"+self.model.texname[0]
        if (self.model.animated):
            self.text_info.text = self.text_info.text+" Animated: True"
        else:
            self.text_info.text = self.text_info.text+" Animated: False"
            
    def setMesh(self, mesh, fformat):
        self.model = mesh
        self.points = self.model.makelist3(self.model.verts)
        self.index = self.model.makelist3(self.model.faces)
        self.normals = self.model.makelist3(self.model.normals)
        self.uv = self.model.makelist2(self.model.uv)
        self.colors=[]
        if (fformat == "obj"):
            self.model.texname = []
            self.model.texname.append('none')
            self.model.xxcount = 0
        #self.model.flipuv()
        #uv=[]
        #colors = [(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1),(1,.5,0),(.5,0,1),(1,1,1),(0,0,0),(1,0,.5),(.5,1,0)]
        colors = []
        self.text_info.text = "Vertices:"+str(len(self.points)/3)+" Faces:"+str(len(self.model.faces))+" XCount:"+str(self.model.xcount)+" XXCount:"+str(self.model.xxcount)+" Tex("+str(len(self.model.texname))+"):"+self.model.texname[0]
        if (self.model.animated):
            self.text_info.text = self.text_info.text+" Animated: True"
            #print 'verts',len(self.points)/3,'vertbone',len(self.model.vertbone)
            #print len(self.model.bones), self.model.bones
            for x in xrange(len(self.model.bones)):
                    colors.append(self.hsv2rgb((float(x)*(360/len(self.model.bones)),1,1)))
                    #print self.hsv2rgb((x*(360/len(self.model.bones)),1,1))
        else:
            self.text_info.text = self.text_info.text+" Animated: False"
        #print colors
        for i in xrange(len(self.points)/3):
            #uv.append(random.randint(0,1)/100)
            #uv.append(random.randint(0,1)/100)
            if (self.model.animated and self.model.vertbone):
                z = self.model.bones[self.model.vertbone[i]]
                self.colors.append(colors[z])
            else:
                self.colors.append((random.randint(5,10)/10,random.randint(5,10)/10,random.randint(5,10)/10))
        self.colors = self.model.makelist3(self.colors)
        self.text_info.x = self.width-5-self.text_info.content_width
        #print self.model.xdata
        if (self.model.xdata):
            self.xdata = self.model.makelist3(self.model.xdata)
        if (self.model.ele1):
            self.ele1 = self.model.ele1
        if (self.model.ele2):
            self.ele2 = self.model.ele2

    def update(self, dt):
	self.t+=1

class TestFrame(wx.Frame):
    
    canvas = ''
    mesh = o3d.Mesh()
    refmesh = o3d.Mesh()
    dlg = 0
    autoload = 0
    flyffdir = 0
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, size=(800, 600))
        self.canvas = TestCanvas(self)

        #read flyff installdir for autoload DDS
        try:
            reg = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software\\INCAInternet\\nProtectGameGuard\\GameMon")
            q = _winreg.QueryValueEx(reg, "CurPath")[0]
            if (q):
                self.flyffdir = '\\'.join(q.split('\\')[:-1])
            
            _winreg.CloseKey(reg)
        except:
            pass

        # events
        self.timer = wx.Timer(self, ID_TIMER)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=ID_TIMER)
        wx.EVT_MENU(self, ID_EXIT, self.MnuQuit)
        wx.EVT_MENU(self, ID_LOAD_O3D, self.FileLoadO3d)
        wx.EVT_MENU(self, ID_LOAD_OBJ, self.FileLoadObj)
        wx.EVT_MENU(self, ID_LOAD_DDS, self.FileLoadDDS)
        wx.EVT_MENU(self, ID_SAVE_OBJ, self.FileSaveObj)
        wx.EVT_MENU(self, ID_SAVE_O3D, self.FileSaveO3d)
        wx.EVT_MENU(self, ID_AUTOLOAD, self.ToggleAutoLoad)
        wx.EVT_MENU(self, ID_ANIMOOTED, self.ToggleAnimated)
        wx.EVT_MENU(self, ID_REF, self.SetMeshType)
        wx.EVT_MENU(self, ID_RENAME, self.RenameO3d)
        wx.EVT_MENU(self, ID_INFO, self.Info)
        wx.EVT_MENU(self, ID_VIEW_POINTS, self.ToggleViewPoints)
        wx.EVT_MENU(self, ID_VIEW_WIRE, self.ToggleViewWire)
        wx.EVT_CLOSE(self, self.OnClose)

        self.timer.Start(75)
        
        #menu items
        menu = wx.Menu()
        menu.Append(ID_LOAD_O3D, "Load O3D", "Do so")
        menu.Append(ID_LOAD_OBJ, "Load OBJ", "Do so")
        menu.AppendSeparator()
        menu.Append(ID_SAVE_O3D, "Save O3D", "Do so")
        menu.Append(ID_SAVE_OBJ, "Save OBJ", "Do so")
        menu.AppendSeparator()
        menu.Append(ID_RENAME, "Rename O3D", "Do so")
        menu.AppendSeparator()
        menu.Append(ID_EXIT, "E&xit", "Terminate the program")

        self.menu2 = wx.Menu()
        self.menu2.Append(ID_LOAD_DDS, "Load DDS", "Do so")
        self.menu2.AppendCheckItem(ID_AUTOLOAD, "Autoload DDS with O3D", "Do so")
        self.menu2.AppendSeparator()
        self.menu2.AppendCheckItem(ID_ANIMOOTED, "Animated", "Do so")
        self.menu2.Append(ID_REF, "Load reference", "Do so")

        menu3 = wx.Menu()
        menu3.Append(ID_INFO, "Info", "bla")

        menu4 = wx.Menu()
        menu4.AppendCheckItem(ID_VIEW_POINTS, "Points", "hi")
        menu4.AppendCheckItem(ID_VIEW_WIRE, "Wireframe", "hi")
        menu4.Check(ID_VIEW_POINTS, True)

        #menubar
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File");
        menuBar.Append(self.menu2, "&Misc.");
        menuBar.Append(menu4, "View");
        menuBar.Append(menu3, "?");
        self.SetMenuBar(menuBar)

        if (not self.flyffdir):
            self.menu2.SetLabel(ID_AUTOLOAD, "Autoload not available")
            self.menu2.Enable(ID_AUTOLOAD, False)
        
        self.dlg = wx.FileDialog(self, "Choose a file", ".", "", "*.o3d", wx.OPEN)
        self.dlg2 = wx.FileDialog(self, "Save as..", ".", "", "*.o3d", wx.SAVE)

    def OnTimer(self, event):
        #self.size=(640,481)
        self.Refresh()

    def MnuQuit(self, event):
        self.Close(1)

    def FileLoadO3d(self, event):
        self.dlg.SetWildcard("*.o3d")
        if (self.dlg.ShowModal() == wx.ID_OK):
            filename = self.dlg.GetPath()
            if (not os.path.exists(filename)):
                wx.MessageBox("File not found.", 'File not found', wx.OK | wx.ICON_EXCLAMATION)
            else:
                self.SetTitle('FlyFF O3D converter - '+self.dlg.GetFilename())
                self.mesh.loadO3d(filename)
                self.canvas.setMesh(self.mesh, "o3d")
                if (self.mesh.animated):
                    self.menu2.Check(ID_ANIMOOTED, True)
            
        if (self.autoload):
            self.canvas.texturename = self.mesh.texname[0]
            if (os.path.exists(self.flyffdir+"\\Model\\Texture\\"+self.mesh.texname[0])):
                self.canvas.bitmap = pyglet.image.load(self.flyffdir+"\\Model\\Texture\\"+self.mesh.texname[0])
                self.canvas.texture = self.canvas.bitmap.get_texture()
            else:
                wx.MessageBox('The given DDS file was not found. If you save, the filename however will be written to the o3d file!', 'File not found', wx.OK | wx.ICON_EXCLAMATION)

    def FileLoadObj(self, event):
        self.dlg.SetWildcard("*.obj")
        if (self.dlg.ShowModal() == wx.ID_OK):
            filename = self.dlg.GetPath()
            if (not os.path.exists(filename)):
                wx.MessageBox("File not found.", 'File not found', wx.OK | wx.ICON_EXCLAMATION)
            else:
                self.SetTitle('FlyFF O3D converter - '+self.dlg.GetFilename())
                self.mesh.loadObj(filename)
                self.menu2.Check(ID_ANIMOOTED, False)
                #print self.mesh.uv
                self.canvas.setMesh(self.mesh, "obj")

    def FileSaveObj(self, event):
        self.dlg2.SetWildcard("*.obj")
        if (self.dlg2.ShowModal() == wx.ID_OK):
            filename = self.dlg2.GetPath()
            self.mesh.saveObj(filename)

    def FileSaveO3d(self, event):
        if (self.canvas.texturename):
            self.dlg2.SetWildcard("*.o3d")
            if (self.dlg2.ShowModal() == wx.ID_OK):
                filename = self.dlg2.GetPath()
                self.mesh.saveO3d(filename, self.dlg2.GetFilename(), self.canvas.texturename)
        else:
            wx.MessageBox('Load a DDS file before saving to o3d.', 'No Texture given', wx.OK | wx.ICON_ERROR)

    def FileLoadDDS(self, event):
        self.dlg.SetWildcard("*.dds")
        if (self.dlg.ShowModal() == wx.ID_OK):
            filename = self.dlg.GetPath()
            self.canvas.texturename = self.dlg.GetFilename()
            if (os.path.exists(filename)):
                self.canvas.bitmap = pyglet.image.load(filename)
                self.canvas.texture = self.canvas.bitmap.get_texture()
            else:
                wx.MessageBox('The given DDS file was not found. If you save, the filename however will be written to the o3d file!', 'File not found', wx.OK | wx.ICON_EXCLAMATION)
                

    def ToggleAutoLoad(self, event):
        if (self.autoload):
            self.autoload = 0
        else:
            self.autoload = 1
            
    def ToggleViewPoints(self, event):
        if (self.canvas.view_points):
            self.canvas.view_points = 0
        else:
            self.canvas.view_points = 1

    def ToggleViewWire(self, event):
        if (self.canvas.view_wire):
            self.canvas.view_wire = 0
        else:
            self.canvas.view_wire = 1

    def ToggleAnimated(self, event):
        if (self.canvas.model.animated):
            self.canvas.model.animated = 0
            self.menu2.Check(ID_ANIMOOTED, False)
            self.canvas.text_boneinfo.text = ''
            
        else:
            self.canvas.model.animated = 1
            self.menu2.Check(ID_ANIMOOTED, True)
            self.canvas.text_boneinfo.text = 'Press right or left arrow key to select points'
            self.canvas.text_boneinfo.x = self.canvas.width-5-self.canvas.text_boneinfo.content_width
        self.canvas.updateInfo()

    def SetMeshType(self, event):
        # load the reference o3d
        self.dlg.SetWildcard("*.o3d")
        if (self.dlg.ShowModal() == wx.ID_OK):
            filename = self.dlg.GetPath()
            if (not os.path.exists(filename)):
                wx.MessageBox("File not found.", 'File not found', wx.OK | wx.ICON_EXCLAMATION)
            elif (not self.canvas.model):
                wx.MessageBox("Load a model file first.", 'Error', wx.OK | wx.ICON_EXCLAMATION)
            else:
                self.refmesh.loadO3d(filename)
                #self.canvas.setMesh(self.mesh, "o3d")
                if (not self.refmesh.animated):
                    self.refmesh.reset()
                    wx.MessageBox('The given O3D File contains no Bone data.','Error', wx.OK | wx.ICON_EXCLAMATION)
                else:
                    #print self.refmesh.bones.keys()
                    self.canvas.model.bones = self.refmesh.bones
                    self.canvas.model.vertbone = []
                    self.canvas.model.xxcount = self.canvas.model.xcount
                    self.canvas.model.itemkind = self.refmesh.itemkind
                    self.canvas.selpoint = 0
                    for x in xrange(len(self.canvas.points)):
                        self.canvas.model.vertbone.append(self.refmesh.bones.keys()[0])
                    colors = []
                    colors2 = []
                    for x in xrange(len(self.refmesh.bones)):
                        colors.append(self.canvas.hsv2rgb((float(x)*(360/len(self.refmesh.bones)),1,1)))
                    for i in xrange(len(self.refmesh.verts)):
                        z = self.refmesh.bones[self.refmesh.vertbone[i]]
                        colors2.append(colors[z])
                    colors = self.refmesh.makelist3(colors2)
                    self.canvas.refcolors = colors
                    self.canvas.refpoints = self.refmesh.makelist3(self.refmesh.verts)
                    self.canvas.refindex = self.refmesh.makelist3(self.refmesh.faces)
                    self.canvas.refnormals = self.refmesh.makelist3(self.refmesh.normals)
                    self.canvas.refuv = self.refmesh.makelist2(self.refmesh.uv)
            
    def RenameO3d(self, event):
        self.dlg.SetWildcard("*.o3d")
        if (self.dlg.ShowModal() == wx.ID_OK):
            filename = self.dlg.GetPath()
            if (not os.path.exists(filename)):
                wx.MessageBox("File not found.", 'File not found', wx.OK | wx.ICON_EXCLAMATION)
            else:
                self.dlg.SetMessage("Saves as..")
                if (self.dlg.ShowModal() == wx.ID_OK):
                    filename2 = self.dlg.GetPath()
                    dial = wx.MessageDialog(None, 'Do you want to keep the original file?', 'Question', wx.YES_NO | wx.ICON_QUESTION)
                    x = dial.ShowModal()
                    if (x == wx.ID_YES):
                        self.mesh.renameO3d(filename,filename2, True)
                    else:
                        self.mesh.renameO3d(filename,filename2, False)
                self.dlg.SetMessage("Chose file..")

    def Info(self, event):
        wx.MessageBox("This program was written by crosbow\ncredits: fatduck\n\n2009", "About")

    def OnClose(self, event):
        # Terminate the Twain Base Class
        self.timer.Stop()
        pyglet.clock.unschedule(self.canvas.update)
        pyglet.app.exit()
        self.Destroy()


class TestApp(wx.App):
    frame = ''
    def OnInit(self):
        self.frame = TestFrame(None, 'FlyFF O3D converter')
        self.SetTopWindow(self.frame)

        self.frame.Show(True)

        # The pyglet thread seems not needed.
        #th = TestThread()
        #th.frame = self.frame
        #th.start()
        
        return True

"""class TestThread(threading.Thread):
    frame = 0
    def run(self):
        pyglet.clock.schedule(self.frame.canvas.update)
        #self.frame.canvas.updater()
        pyglet.app.run()"""
        

if __name__ == '__main__':
    TestApp(redirect=False).MainLoop()
    #TestThread().start()
