#!/usr/bin/env python3

import sys, os, codecs
from tkinter import Tk, PhotoImage
from xml.dom.minidom import parse
from idlelib.TreeWidget import TreeItem, TreeNode, ScrolledCanvas

# <item content="" icon="none" branch="close" block="narrow" level="0" IsShown="true" IsBold="false" ShowBranch="false" TextColor="00000000" BkgrdColor="ffffff00" ModifyTime="2012-02-19 15:40:18" IsFile="false">
bnIcons = ('none', 'flag', 'tick', 'cross', 'star', 'question', 'warning', 'idea')
booAttributes = ('content', 'icon', 'branch', 'block', 'level', 'IsShown', 'IsBold', 'ShowBranch', 'TextColor', 'BkgrdColor', 'ModifyTime', 'IsFile')

class BooTreeItem(TreeItem):
    """TreeItem implemention of BooguNote boo file"""
    def __init__(self, node, dom, filePath):
        super().__init__()
        self.node = node
        self.dom = dom
        self.filePath = filePath
        self.defaultNode = parse('defaultNode.boo').childNodes[0]

    def GetText(self):
        return self.getValue('content')

    # def GetLabelText(self):
    #     return 'Label Text'

    def IsEditable(self):
        return True

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
        prelist = [BooTreeItem(node, self.dom, self.filePath) for node in children]
        itemlist = [item for item in prelist if item.GetText()]
        return itemlist

    # def OnDoubleClick(self):
    #     pass

    def setIcon(self, newIcon):
        self.setValue('icon', newIcon)

    def getValue(self, booAttribute):
        node = self.node
        if node.nodeType == node.ELEMENT_NODE and node.nodeName == 'item' and booAttribute in booAttributes:
            for (name, value) in node.attributes.items():
                if name == booAttribute:
                    return value

    def setValue(self, booAttribute, newValue):
        node = self.node
        if node.nodeType == node.ELEMENT_NODE and node.nodeName == 'item' and booAttribute in booAttributes:
            node.attributes[booAttribute] = newValue
            self.writeDom2File()
        else:
            print('Error on setting value:', booAttribute, newValue)

    def writeDom2File(self):
        f = codecs.open(self.filePath, 'w', 'utf-8')
        f.write(self.dom.toxml())
        f.close()

    def addChild(self):
        parent = self.node
        child = self.dom.importNode(self.defaultNode, True)
        parent.appendChild(child)
        self.writeDom2File()
        child = BooTreeItem(parent, self.dom, self.filePath)
        child.setValue('level', str(int(self.getValue('level')) + 1))

    def deleteNode(self):
        node = self.node
        parent = self.node.parentNode
        parent.removeChild(node)
        self.writeDom2File()
        parent = BooTreeItem(parent, self.dom, self.filePath)


class BooTreeNode(TreeNode):
    """Extends the built-in TreeNode class to display BooguNote icons"""
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
        self.canvas.bind("<Control-KeyPress-]>", self.nextIcon)
        self.canvas.bind("<Control-KeyPress-[>", self.prevIcon)
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
                            return bnIcons[i-1]
                    else:
                        print('Invalid direction:', direction)    
        else:
            print('Not selected!')

    def nextIcon(self, event):
        newIcon = self.getNewIcon('next')
        self.item.setIcon(newIcon)
        self.redrawIcon()

    def prevIcon(self, event):
        newIcon = self.getNewIcon('prev')
        self.item.setIcon(newIcon)
        self.redrawIcon()

    def addAfter(self, event):
        print('addAfter')

    def addBefore(self, event):
        print('addBefore')

    def addChild(self, event):
        self.item.addChild()
        self.item.GetSubList()
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
        self.item.GetSubList()
        pyBn.refresh()

class PyBooguNote():

    def __init__(self, boo = 'test_files/test.boo'):
        self.root = Tk()
        self.root.configure(bd=0, bg="yellow")
        self.root.focus_set()
        self.sc = ScrolledCanvas(self.root, bg="white", highlightthickness=0, takefocus=1)
        self.sc.frame.pack(expand=1, fill="both")
        self.boo = boo

    def refresh(self, clear = True):
        if clear:
            del(self.dom)
            del(self.item)
            del(self.node)
        self.dom = parse(self.boo)
        self.item = BooTreeItem(self.dom.documentElement, self.dom, self.boo)
        self.node = BooTreeNode(self.sc.canvas, None, self.item)
        self.node.expand()


if __name__ == '__main__':
    pyBn = PyBooguNote()
    pyBn.refresh(False)
    pyBn.root.mainloop()
