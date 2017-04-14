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
    Qt,QTime
)

from PyQt5.QtTest import QTest

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
    def __init__( self, parent, the_settings ) :
        super().__init__( parent )
        # Save link to main window
        self.main_window = parent
        # Save link to settings object
        self.settings = the_settings
        # Get the status bar
        self.status_bar = parent.statusBar()
        # just the time
        self.time = QTime()
        self.time.start()
        # Slot that will point to a QAudioInput some day
        self.input_device = None
        # Slot that will point to a QAudioOutput in time
        self.otput_device = None
        # set up layout, creating:
        #   self.input_info_list, list of QAudioInfo for inputs
        #   self.cb_inputs, combox of input names in same order
        #   self.otput_info_list, list of QAudioInfo for outputs
        #   self.cb_otputs, combox of output names in same order
        #   self.volume, volume slider
        #   self.mute, mute checkbox
        self._uic()
        # Connect up signals to slots. Up to this point, the changes that
        # _uic() made in e.g. the volume or mute, or the combobox selections,
        # raised signals that were not connected. Now connect the signals
        # so that user-changes go to our slots for handling.
        # Mute button goes to mute_change
        self.mute.stateChanged.connect( self.mute_change )
        # Change in volume goes to volume_change
        self.volume.valueChanged.connect( self.volume_change )
        # Changes in the combox selections go to in_device and ot_device
        self.cb_inputs.currentIndexChanged.connect( self.in_dev_change )
        self.cb_otputs.currentIndexChanged.connect( self.ot_dev_change )
        # Now pretend the user has made a selection of the in and out devices.
        # That should result in activating everythings.
        self.in_dev_change( self.cb_inputs.currentIndex() )
        self.ot_dev_change( self.cb_otputs.currentIndex() )


    # Method to disconnect the input and output devices, if they exist.
    # This is called prior to any change in device selection.
    # Note that the QWidget class has an existing method disconnect(),
    # and we do not want to override that so that name is not used.

    def disconnect_devices( self ) :

        # If an output device exists, make it stop. That prevents it
        # trying to pull any data from the input device if any.
        if self.otput_device is not None :
            self.otput_device.stop()
        # If an input device exists, make it stop also. That means it
        # loses track of the output device it was formerly connected to.
        if self.input_device is not None :
            self.input_device.stop()

    # Method to connect the input and output devices, if both exist. This is
    # called after making any change in device selection.

    def reconnect_devices( self ) :

        if (self.input_device is not None) \
           and (self.otput_device is not None ) :

            # Connect the devices by asking the OUTput device for its
            # QIODevice, and passing that to the INput device's start()
            # method. This could equally well be done the other way,
            # by passing the input dev's IODevice to the output device.

            self.input_device.start( self.otput_device.start() )
            #self.otput_device.start( self.input_device.start() )

            # In case the output device was just created, set its volume.
            self.set_volume()

    # Method to set the volume on the output device. (The input device volume
    # is always 1.0.) This is called on any change of the volume slider or
    # of the Mute button or of the output device choice.

    def set_volume( self ) :
        if self.mute.isChecked() :
            # Mute is ON, set volume to 0 regardless of volume slider
            volume = 0.0
        else :
            # Mute is OFF, set volume to float version of volume slider
            volume = self.volume.value() / 100
        if self.otput_device :
            # an output device exists (almost always true), set it
            self.otput_device.setVolume( volume )

    # Slot entered upon any change in the volume slider widget.
    def volume_change( self, new_level ) :
        if self.mute.isChecked() :
            # The Mute button is ON; assume the user wants it OFF, else why
            # move the slider? Note this causes a call to set_volume().
            self.mute.setChecked( False )
        else :
            # The Mute button is OFF, just change the volume.
            self.set_volume()

    # Slot entered upon toggling of the mute switch, by the user or by the
    # code calling mute.setChecked(). Make sure the volume is set appropriately.
    def mute_change( self, onoff ) :
        self.set_volume()

    # Slots for selection of the input and output devices. On startup we have
    # neither an input nor an output device. We do not know which combox the
    # user will fiddle with first.

    # Slot entered upon any change in the selection of the input device
    # combo box. The argument is the new index of the list of values.

    def in_dev_change( self, new_index ) :

        # Disconnect and stop the devices if they are connected.
        self.disconnect_devices()

        self.input_device = None # device object goes out of scope

        # Get the QAudioDeviceInfo corresponding to this index of the combox.
        audio_info = self.input_info_list[ new_index ]

        # Create a new QAudioInput based on that.
        preferred_format = audio_info.preferredFormat()
        self.input_device = QAudioInput( audio_info, preferred_format )

        # the input device volume is always 1.0, wide open.
        self.input_device.setVolume( 1.0 )

        # The choice of buffer size has a major impact on the lag. It needs
        # to be small or there is severe echo; but if it is too small, there
        # is a sputtering or "motor-boating" effect.
        self.input_device.setBufferSize( 384 )

        # hook up possible debug status display
        self.input_device.stateChanged.connect(self.in_dev_state_change)

        # reconnect the devices if possible.

        self.reconnect_devices()

    # Slot entered upon any change in the selection of output. The argument
    # is the index to the list of output devices in the combobox.

    def ot_dev_change( self, new_index ) :
        print('index',new_index)
        # Disconnect and stop the devices if they are connected.
        self.disconnect_devices()

        self.otput_device = None # device object goes out of scope

        # Get the QAudioDeviceInfo corresponding to this index of the combox.
        audio_info = self.otput_info_list[ new_index ]

        # Create a new QAudioOutput based on that.
        preferred_format = audio_info.preferredFormat()
        self.otput_device = QAudioOutput( audio_info, preferred_format )
        self.otput_device.setVolume( 0 ) # reconnect will set correct volume

        # hook up possible debug status display
        self.otput_device.stateChanged.connect(self.ot_dev_state_change)

        # reconnect the devices if possible. Which also sets the volume.

        self.reconnect_devices()


    # Show some text in the main-window status bar for 1 second, more or less.
    def show_status( self, text, duration=1000 ):
        self.status_bar.showMessage( text, duration )

    # Slots called on any "state" change of an audio device. Optionally
    # show the state in the main window status bar.
    def in_dev_state_change( self, new_state):
        #self.show_status(
            #'{} in dev state {}'.format(self.time.elapsed(),int(new_state))
        #)
        pass
    def ot_dev_state_change( self, new_state):
        #self.show_status(
            #'{} ot dev state {}'.format(self.time.elapsed(),int(new_state))
        #)
        pass

    # Close events are only received by a top-level widget. When our top-level
    # widget gets one, indicating the app is done, it calls this method.

    def closeEvent( self, event ) :
        # if we have devices, make them stop.
        self.disconnect_devices()

        # if the devices exist, reset them and then trash them.
        if self.otput_device is not None:
            self.otput_device.reset()
            self.otput_device = None
        if self.input_device is not None:
            self.input_device.reset()
            self.input_device = None

        # Save the current selection of the input and output combo boxes,
        # in the settings file.
        in_dev_name = self.cb_inputs.currentText()
        self.settings.setValue( 'in_dev_name', in_dev_name )
        ot_dev_name = self.cb_otputs.currentText()
        self.settings.setValue( 'ot_dev_name', ot_dev_name )

        # Save the volume setting and mute status in the settings.
        self.settings.setValue( 'volume', self.volume.value() )
        self.settings.setValue( 'mute_status', int( self.mute.isChecked() ) )

    def _uic( self ) :
        '''
    set up our layout which consists of:

                 Big Honkin' Label
        [input combobox]    [output combobox]
               [volume slider]  [x] Mute

    Hooking the signals to useful slots is the job
    of __init__. Here just make the layout.
        '''
        self.setMinimumWidth(400)
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
        if 0 == len(self.input_info_list) :
            self.input_info_list = [ QAudioDeviceInfo.defaultInputDevice() ]
        # Make a list of the name-strings for those items.
        in_dev_names = [ audio_info.deviceName() for audio_info in self.input_info_list ]
        # Create a combo box and populate it with those names
        self.cb_inputs = QComboBox()
        self.cb_inputs.addItems( in_dev_names )
        # If the in_dev_name from the previous run is in the current list,
        # make it current, otherwise pick the first item.
        in_dev_name = self.settings.value( 'in_dev_name', 'unknown' )
        if in_dev_name in in_dev_names :
            self.cb_inputs.setCurrentIndex( in_dev_names.index( in_dev_name ) )
        else :
            self.cb_inputs.setCurrentIndex( 0 )

        # Create a list of QAudioInfo objects for outputs
        self.otput_info_list = QAudioDeviceInfo.availableDevices( QAudio.AudioOutput )
        if 0 == len( self.otput_info_list ) :
            self.otput_info_list = [ QAudioDeviceInfo.defaultOutputDevice() ]
        # Make a list of the name-strings of those things
        ot_dev_names = [ audio_info.deviceName() for audio_info in self.otput_info_list ]
        # Create a combo box and populate it with those names
        self.cb_otputs = QComboBox()
        self.cb_otputs.addItems( ot_dev_names )
        # If the ot_dev_name from the previous run is in the current list,
        # make it the current choice in the box.
        ot_dev_name = self.settings.value( 'ot_dev_name', 'unknown' )
        if ot_dev_name in ot_dev_names :
            self.cb_otputs.setCurrentIndex( ot_dev_names.index( ot_dev_name ) )
        else :
            self.cb_otputs.setCurrentIndex( 0 )

        #self.show_status(
            #'{} inputs {} otputs'.format(len(self.input_info_list),len(self.otput_info_list))
        #)
        # Create a combo box and populate it with names of outputs

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
        # set the volume slider to the value from the previous run, or zero.
        self.volume.setValue( self.settings.value( 'volume', 0 ) )

        # Create a checkbox "Mute"
        self.mute = QCheckBox( 'Mute' )
        # Set it to the value at the end of the last run, or to True
        self.mute.setChecked( bool( self.settings.value( 'mute_status', 1 ) ) )

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

# Define a main window subclass so as to receive close events, mainly.
# Initialization input is the settings object.

class MyMainWindow( QMainWindow ) :
    def __init__( self, the_settings ) :
        super().__init__( None ) # parentless main window

        # Create the real widget and set it as our central widget.
        self.sidetone = SideToneWidget( self, the_settings )
        self.setCentralWidget( self.sidetone )

    # Define a custom closeEvent handler. When the app is terminated
    # this is called. Just pass the call on to the closeEvent in the
    # sideTone widget. Note: I don't know why but this is entered twice.
    # That's harmless but annoying.

    def closeEvent( self, event ) :
        self.sidetone.closeEvent( event )
        super().closeEvent( event ) # go ahead and close now

def main():
    import sys
    import icon
    # Start the application. This does a ton of Qt setup stuff.
    the_app = QApplication(sys.argv)
    QTest.qWait( 500 ) # idle for half a second before doing stuff

    '''
    With the application started, set the constants that define where
    the settings file is stored and what it is called. Then open the settings.

    FYI: Locations for Qt settings values:
                    Linux: $HOME/.config/TassoSoft/Sidetone.conf
                  Mac OSX: $HOME/Library/Preferences/com.TassoSoft.Sidetone.plist
    Windows (registry): HKEY_CURRENT_USER\Software\TassoSoft\Sidetone

    '''

    the_app.setOrganizationName( "TassoSoft" )
    the_app.setOrganizationDomain( "tassos-oak.com" )
    the_app.setApplicationName( "Sidetone" )

    from PyQt5.QtCore import QSettings
    the_settings = QSettings()
    '''
    Uncomment the following to wipe all settings everything back to defaults.
    '''
    #the_settings.clear()

    main = MyMainWindow( the_settings )
    main.show()
    the_app.exec_()
    QTest.qWait( 500 ) # idle for half a second to let Python shut down

if __name__ == '__main__' :
    main()
