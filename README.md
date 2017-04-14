# Sidetone

This app has only been tested in Mac OS 10.10, because that's the only place I'll use it.
In theory it should work on other platforms.

"Sidetone" is the sound of your voice in a mic, reproduced in your headphones or the 
earpiece of a telephone handset.
It lets you know the mic is working and makes your voice less muffled, so you speak at a normal volume.

When started the app presents a small window with two menus,
one to select an available input audio source,
and one to select an available output destination.
Typically the input and output would both be your headset with its boom mike.
However, you might be using headphones and a stand-alone mic.
Whatever.

After selecting the input and output, click to turn off the Mute checkbox.
Adjust the volume slider while speaking into the mic.
You should hear your own voice in the output with minimal latency.

The choice of in/out devices and the volume and mute settings are remembered
and restored on the next run.

You need to have PyQt5 and Python 3.4+ installed. Then start the app using

    python sidetone.py


*Hey, apologies to the person who submitted a pull request to add info to this
readme. I stupidly did a push of new code before updating my master, and wiped
out the merged pull. Feel free to submit another.*
