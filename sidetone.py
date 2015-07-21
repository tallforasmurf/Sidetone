'''

Provide controllable sidetone from an input device, presumably a mic,
to an output device, presumably headphones.

Gets names of all available audio inputs and outputs.
Populates comboboxes with names of available audio devices.
When user selects a device, notes it. When both an input and
an output are selected, corresponding audio devices are created
and connected. The user can control the volume with a slider and
mute with a checkbox.

'''
from PyQt5.QtCore import (
    Qt
)

from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget
)
from PyQt5.QtMultimedia import (
    QAudio,
    QAudioDeviceInfo,
    QAudioInput,
    QAudioOutput
)

class SideToneWidget( QWidget ) :
    def __init__( self, parent ) :
        super().__init__( parent )
        # Slot that will point to a QAudioInput some day
        self.input_device = None
        # Slot that will point to a QAudioOutput in time
        self.otput_device = None
        # set up layout, creating:
        # self.input_info_list, list of QAudioInfo for inputs
        # self.cb_inputs, combox of input names in same order
        # self.otput_info_list, list of QAudioInfo for outputs
        # self.cb_otputs, combox of output names in same order
        # self.volume, volume slider
        # self.mute, mute checkbox
        self._uic()
        # Connect up signals to slots.
        # Changes in the comboxes go to in_device and ot_device
        self.cb_inputs.currentIndexChanged.connect( self.in_dev_change )
        self.cb_otputs.currentIndexChanged.connect( self.ot_dev_change )
        # Mute button goes to mute_change
        self.mute.stateChanged.connect( self.mute_change )
        # Change in volume goes to volume_change
        self.volume.valueChanged.connect( self.volume_change )
        # Start with the mute switch on. This triggers the above two signals.
        self.mute.setChecked( True )

    # Slot for any change in volume (or mute). If we have an output device
    # then convert level to a real and pass to the output device. If the new
    # level is 0, tell the device to stop; if nonzero, tell it to start.
    # Note we don't do anything about the input device level, it is always 1.0
    def volume_change( self, new_level ) :
        if self.otput_device : # we have an output device
            self.otput_device.setVolume( self.volume.value() / 100 )
            if new_level == 0 : # looks like a mute
                # tell the output device to stop just in case it
                # doesn't know about volume control.
                self.otput_device.stop()
            else : # non-zero level, if the output is stopped, start it
                if self.otput_device.state() == QAudio.StoppedState :
                    self.otput_device.start()

    # Slot for mute switch. Note that any change to the volume slider
    # generates a signal to the volume_change slot.
    def mute_change( self, onoff ) :
        if onoff :
            # Mute has been clicked ON. Remember the current volume.
            # Turn the volume to zero.
            self.volume_level = self.volume.value()
            self.volume.setValue( 0 )
        else :
            # Mute has been clicked OFF. If we do not yet have input and
            # output devices, get them. Then reset the old volume level.
            if self.otput_device is None :
                # We are starting up and have no devices. Fake a call to
                # the checkbox-change entries thus creating devices.
                self.in_dev_change( self.cb_inputs.currentIndex() )
                self.ot_dev_change( self.cb_inputs.currentIndex() )
            self.volume.setValue( self.volume_level )

    # Slots for changes in the selection of the input- and output-device
    # combo boxes. On startup we have neither an input nor an output device.
    # We do not know which combox the user will fiddle with first. So either
    # has to assume that the other device may not yet exist.
    #
    # On a change of input choice: if we have an input device, get rid of it.
    # Create a new input device. Set its level to 1.0. If we
    # have an output, connect the two.

    def in_dev_change( self, new_index ) :
        if self.input_device :
            if self.otput_device :
                self.otput_device.stop()
            self.input_device.stop()
            self.input_device = None # goodby object
        # Get the QAudioDeviceInfo corresponding to this index of the combox.
        audio_info = self.input_info_list[ new_index ]
        # Create a new QAudioInput based on that.
        preferred_format = audio_info.preferredFormat()
        self.input_device = QAudioInput( audio_info, preferred_format )
        self.input_device.setVolume( 1.0 )
        self.input_device.setBufferSize( 384 )
        # If we have an output device, redirect it to this input. This is
        # done by asking the input device for its QIODevice, and passing that
        # to the output device's start() method.
        if self.otput_device :
            self.input_device.start( self.otput_device.start() )
            #self.otput_device.start( self.input_device.start() )

    # On a change in the selection of output choice: If we have an output
    # device, get rid of it. Create a new output device. If we have an input
    # device, connect the two. Set the output level from the volume slider.

    def ot_dev_change( self, new_index ) :
        if self.otput_device :
            if self.input_device :
                self.input_device.stop()
            self.otput_device.stop()
            self.otput_device = None
        audio_info = self.otput_info_list[ new_index ]
        preferred_format = audio_info.preferredFormat()
        self.otput_device = QAudioOutput( audio_info, preferred_format )
        self.otput_device.setVolume( self.volume.value() / 100 )
        #self.otput_device.setBufferSize( 384 )
        if self.input_device :
            self.input_device.start( self.otput_device.start() )
            #self.otput_device.start( self.input_device.start() )



    def _uic( self ) :
        '''
    set up our layout which consists of:

                 Big Honkin' Label
        [input combobox]    [output combobox]
               [volume slider]  [x] Mute

    hooking put the signals to useful slots is the job
    of __init__. Here just make the layout.
        '''
        # Create the big honkin' label and logo
        icon_pixmap = QPixmap( ':/icon.png' ).scaledToWidth(64)
        icon_label = QLabel()
        icon_label.setPixmap( icon_pixmap )
        text_label = QLabel("Sidetone!")
        hb_label = QHBoxLayout()
        hb_label.addStretch(1)
        hb_label.addWidget( icon_label , 0 )
        hb_label.addWidget( text_label , 0 )
        hb_label.addStretch(1)

        # Create a list of QAudioInfo objects for inputs
        self.input_info_list = QAudioDeviceInfo.availableDevices( QAudio.AudioInput )
        # Create a combo box and populate it with names of inputs
        self.cb_inputs = QComboBox()
        self.cb_inputs.addItems(
            [ audio_info.deviceName() for audio_info in self.input_info_list ]
            )
        # Create a list of QAudioInfo objects for outputs
        self.otput_info_list = QAudioDeviceInfo.availableDevices( QAudio.AudioOutput )
        # Create a combo box and populate it with names of outputs
        self.cb_otputs = QComboBox()
        self.cb_otputs.addItems(
            [ audio_info.deviceName() for audio_info in self.otput_info_list ]
            )
        # Lay those two out aligned to the outside
        hb_combos = QHBoxLayout()
        hb_combos.addWidget( self.cb_inputs, 1 )
        hb_combos.addStretch( 0 )
        hb_combos.addWidget( self.cb_otputs, 1 )
        # Create a volume slider from 0 to 100.
        self.volume = QSlider( Qt.Horizontal, self )
        self.volume.setMinimum( 0 )
        self.volume.setMaximum( 100 )
        self.volume.setTickInterval( 10 )
        self.volume.setTickPosition( QSlider.TicksBothSides )
        # Create a checkbox "Mute"
        self.mute = QCheckBox( 'Mute' )
        # Put those together in a row squeezed in the center
        hb_volume = QHBoxLayout()
        hb_volume.addStretch( 1 )
        hb_volume.addWidget( self.volume, 1 )
        hb_volume.addWidget( self.mute, 0)
        hb_volume.addStretch( 1 )
        # Stack all those up as this widget's layout
        vlayout = QVBoxLayout()
        vlayout.addLayout( hb_label )
        vlayout.addLayout( hb_combos )
        vlayout.addLayout( hb_volume )
        self.setLayout( vlayout )
        # end of _uic

def main():
    import sys
    import icon
    app = QApplication(sys.argv)

    main = QMainWindow()
    central = SideToneWidget( main )
    main.setCentralWidget( central )
    main.show()
    app.exec_()

if __name__ == '__main__' :
    main()
