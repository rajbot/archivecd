#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
import sys

# ArchiveWizard
#_________________________________________________________________________________________
class ArchiveWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)

        self.intro_page        = IntroPage(self)
        self.scan_drives_page  = ScanDrivesPage(self)
        self.read_toc_page     = ReadTOCPage(self)

        self.addPage(self.intro_page)
        self.addPage(self.scan_drives_page)
        self.addPage(self.read_toc_page)


# WizardPage
#_________________________________________________________________________________________
class WizardPage(QtGui.QWizardPage):
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.wizard = parent


# IntroPage
#_________________________________________________________________________________________
class IntroPage(WizardPage):
    def __init__(self, wizard):
        WizardPage.__init__(self, wizard)
        self.setTitle('Introduction')

        #Check to ensure we are on Windows
        if sys.platform != 'win32':
            error_str = 'This program must be run on a Windows computer.'
            self.setSubTitle(error_str)
            return

        self.setSubTitle('Please enter a CD and click the Next button')


    def isComplete(self):
        return (sys.platform == 'win32')


# ScanDrivesPage
#_________________________________________________________________________________________
class ScanDrivesPage(WizardPage):
    def __init__(self, wizard):
        WizardPage.__init__(self, wizard)
        self.setTitle('Checking for CD Drives')
        
        layout = QtGui.QVBoxLayout()
        self.combo = QtGui.QComboBox()
        self.combo.addItems(['(Choose CD Drive)'])
        self.connect(self.combo, QtCore.SIGNAL("currentIndexChanged(const QString&)"),
                     self, QtCore.SIGNAL("completeChanged()"))


        layout.addWidget(self.combo)
        self.setLayout(layout)


    def initializePage(self):
        #based on picard/util/cdrom.py
        from ctypes import windll
        GetLogicalDrives = windll.kernel32.GetLogicalDrives
        GetDriveType = windll.kernel32.GetDriveTypeA
        DRIVE_CDROM = 5
        cd_drives = []
        mask = GetLogicalDrives()
        for i in range(26):
            if mask >> i & 1:
                drive = chr(i + ord("A")) + ":"
                if GetDriveType(drive) == DRIVE_CDROM:
                    cd_drives.append(drive)
        self.combo.addItems(cd_drives)



    def isComplete(self):
        print self.combo.currentIndex()
        return (self.combo.currentIndex() != 0)



# ReadTOCPage
#_________________________________________________________________________________________
class ReadTOCPage(WizardPage):
    def __init__(self, wizard):
        WizardPage.__init__(self, wizard)
        self.setTitle('Looking up CD in IA database')

        self.toc_label = QtGui.QLabel('checking...')
        self.toc_string = None
        self.is_complete = False

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toc_label)

        self.setLayout(layout)


    def isComplete(self):
        return self.is_complete


    def initializePage(self):
        cd_drive = self.wizard.scan_drives_page.combo.currentText()
        print cd_drive
        self.toc_label.setText('reading ' + cd_drive)
        import discid
        try:
            disc = discid.read(str(cd_drive))
        except discid.disc.DiscError:
            self.toc_label.setText('Unable to read disc')
            return

        self.toc_string = disc.toc_string

        print self.toc_string
        self.toc_label.setText(self.toc_string)
        self.is_complete = True


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    wizard = ArchiveWizard()
    sys.exit(wizard.exec_())
