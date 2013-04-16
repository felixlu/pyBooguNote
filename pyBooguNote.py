#!/usr/bin/env python3

import sys, os, codecs
from tkinter import Tk, Frame, PhotoImage, Button
from tkinter.filedialog import askopenfilename, asksaveasfilename
from xml.dom.minidom import parse, parseString
from idlelib.TreeWidget import TreeItem, TreeNode, ScrolledCanvas

bnIcons = ('none', 'flag', 'tick', 'cross', 'star', 'question', 'warning', 'idea')
booAttributes = ('content', 'icon', 'branch', 'block', 'level', 'IsShown', 'IsBold', 'ShowBranch', 'TextColor', 'BkgrdColor', 'ModifyTime', 'IsFile')
defaultNode = parseString('<item content="New Node" icon="none" branch="close" block="narrow" level="0" IsShown="true" IsBold="false" ShowBranch="false" TextColor="00000000" BkgrdColor="ffffff00" ModifyTime="2012-02-19 15:40:18" IsFile="false" />').firstChild
defaultFile = parseString('''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<root DefaultSaveDir="" DefaultSaveExtension="png" version="7">
  <item content="New Node" icon="none" branch="close" block="narrow" level="0" IsShown="true" IsBold="false" ShowBranch="false" TextColor="00000000" BkgrdColor="ffffff00" ModifyTime="2012-02-19 15:40:18" IsFile="false" />
</root>''')

class BooTreeItem(TreeItem):
    """TreeItem implemention of BooguNote boo file, with xml.dom.minidom"""
    def __init__(self, file_path, dom, node):
        super().__init__()
        self.file_path = file_path
        self.dom = dom
        self.node = node

    def GetText(self):
        node = self.node
        if node.nodeType == node.ELEMENT_NODE:
            if node.nodeName == 'item':
                return self.getValue('content')
            elif node.nodeName == 'root':
                return ' '

    # def GetLabelText(self):
    #     return 'Label Text'

    def IsEditable(self):
        node = self.node
        return node.nodeType == node.ELEMENT_NODE and node.nodeName == 'item'

    def SetText(self, text):
        return self.setValue('content', text)

    def GetIconName(self):
        return self.getValue('icon')

    # def GetSelectedIconName(self):
    #     pass

    def IsExpandable(self):
        return self.node.hasChildNodes()

    def GetSubList(self):
        parent = self.node
        children = parent.childNodes
        prelist = [BooTreeItem(self.file_path, self.dom, node) for node in children]
        itemlist = [item for item in prelist if item.GetText()]
        return itemlist

    # def OnDoubleClick(self):
    #     pass

    def setIcon(self, newIcon):
        self.setValue('icon', newIcon)

    def getValue(self, booAttribute):
        node = self.node
        if node.nodeType == node.ELEMENT_NODE and node.nodeName == 'item':
            if booAttribute in booAttributes:
                for (name, value) in node.attributes.items():
                    if name == booAttribute:
                        return value
            else:
                print('Error on getting value:', booAttribute)

    def setValue(self, booAttribute, newValue):
        node = self.node
        if node.nodeType == node.ELEMENT_NODE and node.nodeName == 'item':
            if booAttribute in booAttributes:
                node.attributes[booAttribute] = newValue
                writeDom2File(self.dom, self.file_path)
            else:
                print('Error on setting value:', booAttribute, newValue)

    def addNode(self, parent, child):
        parent.appendChild(child)
        writeDom2File(self.dom, self.file_path)
        curItem = BooTreeItem(self.file_path, self.dom, child)
        curItem.setValue('IsShown', 'true')
        curItem.setValue('branch', 'open')
        return curItem

    def addChild(self):
        parent = self.node
        child = self.dom.importNode(defaultNode, True)
        child = self.addNode(parent, child)
        parent_level = self.getValue('level')
        if parent_level:
            parent_level = int(parent_level)
        else:
            parent_level = -1
        child.setValue('level', str(parent_level + 1))
        self.setValue('branch', 'open')

    def addAfter(self):
        parent = self.node.parentNode
        child = self.dom.importNode(defaultNode, True)
        child = self.addNode(parent, child)
        child.setValue('level', self.getValue('level'))

    def addBefore(self):
        pass

    def deleteNode(self):
        node = self.node
        parent = self.node.parentNode
        parent.removeChild(node)
        writeDom2File(self.dom, self.file_path)
        parent = BooTreeItem(self.file_path, self.dom, parent)
        curItem = parent


class BooTreeNode(TreeNode):
    """Extension of the built-in TreeNode class, to provide BooguNote UI interaction features"""
    def __init__(self, canvas, parent, item):
        super(BooTreeNode, self).__init__(canvas, parent, item)
        self.canvas = canvas
        self.parent = parent
        self.item = item
        self.iconimages = {}

    def geticonimage(self, name):
        try:
            return self.iconimages[name]
        except KeyError:
            pass
        if name in bnIcons:
            file, ext = os.path.splitext(name)
            ext = ext or ".gif"
            iconPath = os.path.join(os.path.dirname(__file__), 'icons')
            fullname = os.path.join(iconPath, file + ext)
            image = PhotoImage(master=self.canvas, file=fullname)
            self.iconimages[name] = image
            return image
        else:
            return super().geticonimage(name)

    def drawicon(self):
        super().drawicon()
        self.canvas.bind("<Control-KeyPress-N>", self.nextIcon)
        self.canvas.bind("<Control-KeyPress-P>", self.prevIcon)
        self.canvas.bind("<Control-KeyPress-Return>", self.addAfter)
        self.canvas.bind("<Control-Shift-KeyPress-Return>", self.addBefore)
        self.canvas.bind("<Shift-KeyPress-Return>", self.addChild)
        self.canvas.bind("<Control-KeyPress-Up>", self.moveUp)
        self.canvas.bind("<Control-KeyPress-Down>", self.moveDown)
        self.canvas.bind("<Control-KeyPress-Left>", self.moveLeft)
        self.canvas.bind("<Control-KeyPress-Right>", self.moveRight)
        self.canvas.bind("<Control-KeyPress-Delete>", self.deleteNode)

    def redrawIcon(self):
        self.canvas.delete(self.image_id)
        self.drawicon()

    def getNewIcon(self, direction):
        if self.selected:
            curIcon = self.item.GetIconName()
            newIcon = ''
            for i in range(len(bnIcons)):
                if bnIcons[i] == curIcon:
                    if direction == 'next':
                        if i == len(bnIcons) - 1:
                            return bnIcons[0]
                        else:
                            return bnIcons[i + 1]
                    elif direction == 'prev':
                        if i == 0:
                            return bnIcons[-1]
                        else:
                            return bnIcons[i - 1]
                    else:
                        print('Invalid direction:', direction)    
        else:
            print('Not selected!')

    def expand(self, event=None):
        super().expand()
        if self.item.getValue('branch') != 'open':
            self.item.setValue('branch', 'open')

    def collapse(self, event=None):
        super().collapse()
        self.item.setValue('branch', 'close')

    def nextIcon(self, event):
        newIcon = self.getNewIcon('next')
        self.item.setIcon(newIcon)
        self.redrawIcon()

    def prevIcon(self, event):
        newIcon = self.getNewIcon('prev')
        self.item.setIcon(newIcon)
        self.redrawIcon()

    def addAfter(self, event):
        self.item.addAfter()
        pyBn.refresh()

    def addBefore(self, event):
        print('addBefore')

    def addChild(self, event):
        self.item.addChild()
        pyBn.refresh()

    def moveUp(self, event):
        print('moveUp')

    def moveDown(self, event):
        print('moveDown')

    def moveLeft(self, event):
        print('moveLeft')

    def moveRight(self, event):
        print('moveRight')

    def deleteNode(self, event):
        self.item.deleteNode()
        pyBn.refresh()

class PyBooguTree():
    """Tree widget"""
    def __init__(self, canvas, file_path, dom):
        self.canvas = canvas
        self.item = BooTreeItem(file_path, dom, dom.documentElement)
        self.refresh(False)

    def refresh(self, clear=True):
        if clear:
            del(self.node)
        self.node = BooTreeNode(self.canvas, None, self.item)
        self.node.expand()
        self.expandChildren(self.node)

    def expandChildren(self, node):
        for child in node.children:
            if child.item.getValue('branch') == 'open':
                child.expand()
                if child.children:
                    self.expandChildren(child)

class PyBooguNote(Frame):
    """Main class"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.create_toolbar()
        self.sc = ScrolledCanvas(parent, bg="white", highlightthickness=0, takefocus=1)
        self.sc.frame.pack(expand=1, fill='both')

    def create_toolbar(self):
        self.toolbar = Frame(self.parent)
        self.btn_new = Button(self.toolbar, text='New', command=self.new_file)
        self.btn_new.grid(row=0, column=0)
        self.btn_open = Button(self.toolbar, text='Open', command=self.open_file)
        self.btn_open.grid(row=0, column=1)
        self.toolbar.pack(fill='both')

    def open_file(self):
        self.file_path = askopenfilename(filetypes=[('BooguNote Files', '.boo')])
        self.dom = parse(self.file_path)
        curItem = None
        pyBt = PyBooguTree(self.sc.canvas, self.file_path, self.dom)
    
    def new_file(self):
        self.file_path = asksaveasfilename()
        print(self.file_path)

def writeDom2File(dom, file_path):
    f = codecs.open(file_path, 'w', 'utf-8')
    dom.writexml(f, encoding='UTF-8')
    f.close()


if __name__ == '__main__':
    app = Tk()
    app.configure(bd=0, bg="yellow")
    app.focus_set()
    pyBn = PyBooguNote(app)
    app.mainloop()
