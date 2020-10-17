# Sidetone - abandoned

"Sidetone" is the sound of your voice in a mic, reproduced in your headphones or the 
earpiece of a telephone handset.
It lets you know the mic is working and makes your voice less muffled, so you speak at a normal volume.

## How it should work

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

# Abandonment

In trying to analyze the problem in the open issue,
I discovered that Sidetone does not work under MacOS 10.14/Mojave, let alone 10.15/Catalina where the issue is seen.
The code runs with no errors reported, but no sound appears in the chosen output device
(unlesss it is also selected as the system output device in Preferences), and the volume and mute widgets have no effect.
I have no clue whatever why this should be.

I suspect that the pitch-shift mentioned in the issue is a result of changes in MacOS 10.15/Catalina,
however as I cannot properly test under Mojave, and don't plan to install Catalina, I can't make progress.

Therefore I am leaving this waif on the curbside for anybody to adopt if they like.
Feel free to clone this repo and fix, improve or extend the code. I am done with it.

# Installation and usage

```bash 
pip3 install PyQt5 # Only needed to install PyQt5 the first time
python3 sidetone.py # Start sidetone
```

Run `nohup python3 sidetone.py &` to background the process and detach it from
the current shell.
