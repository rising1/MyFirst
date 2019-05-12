from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

def videofig(num_frames, redraw_func, play_fps=25, big_scroll=30, key_func=None, *args):
  """Figure with horizontal scrollbar and play capabilities
  
  This script is mainly inspired by the elegant work of João Filipe Henriques
    https://www.mathworks.com/matlabcentral/fileexchange/29544-figure-to-play-and-analyze-videos-with-custom-plots-on-top?focused=5172704&tab=function
    
  :param num_frames: an integer, number of frames in a sequence
  :param redraw_func: callable with signature redraw_func(f, axes)
                      used to draw a new frame at position f using axes, which is a instance of Axes class in matplotlib 
  :param play_fps: an integer, number of frames per second, used to control the play speed
  :param big_scroll: an integer, big scroll number used when pressed page down or page up keys. 
  :param key_func: optional callable which signature key_func(key), used to provide custom key shortcuts.
  :param args: other optional arguments
  :return: None
  """
  # Check arguments
  check_int_scalar(num_frames, 'num_frames')
  check_callback(redraw_func, 'redraw_func')
  check_int_scalar(play_fps, 'play_fps')
  check_int_scalar(big_scroll, 'big_scroll')
  if key_func:
    check_callback(key_func, 'key_func')

  # Initialize figure
  fig_handle = plt.figure()

  # main drawing axes for video display
  axes_handle = plt.axes([0, 0.03, 1, 0.97])
  axes_handle.set_axis_off()

  # Build scrollbar
  scroll_axes_handle = plt.axes([0, 0, 1, 0.03], facecolor='lightgoldenrodyellow')
  scroll_handle = Slider(scroll_axes_handle, '', 0.0, num_frames - 1, valinit=0.0)

  def draw_new(_):
    # Set to the right axes and call the custom redraw function
    plt.sca(axes_handle)
    redraw_func(int(scroll_handle.val), axes_handle)
    fig_handle.canvas.draw_idle()

  def scroll(new_f):
    new_f = min(max(new_f, 0), num_frames - 1)  # clip in the range of [0, num_frames - 1]
    cur_f = scroll_handle.val

    # Stop player at the end of the sequence
    if new_f == (num_frames - 1):
      play.running = False

    if cur_f != new_f:
      # move scroll bar to new position
      scroll_handle.set_val(new_f)

    return axes_handle

  def play(period):
    play.running ^= True  # Toggle state
    if play.running:
      frame_idxs = range(int(scroll_handle.val), num_frames)
      play.anim = FuncAnimation(fig_handle, scroll, frame_idxs,
                                interval=1000 * period, repeat=False)
      plt.draw()
    else:
      play.anim.event_source.stop()

  # Set initial player state
  play.running = False

  def key_press(event):
    key = event.key
    f = scroll_handle.val
    if key == 'left':
      scroll(f - 1)
    elif key == 'right':
      scroll(f + 1)
    elif key == 'pageup':
      scroll(f - big_scroll)
    elif key == 'pagedown':
      scroll(f + big_scroll)
    elif key == 'home':
      scroll(0)
    elif key == 'end':
      scroll(num_frames - 1)
    elif key == 'enter':
      play(1 / play_fps)
    elif key == 'backspace':
      play(5 / play_fps)
    else:
      if key_func:
        key_func(key)

  # Register events
  scroll_handle.on_changed(draw_new)
  fig_handle.canvas.mpl_connect('key_press_event', key_press)

  # Draw initial frame
  redraw_func(0, axes_handle)

  # Start playing
  play(1 / play_fps)

  # plt.show() has to be put in the end of the function,
  # otherwise, the program simply won't work, weird...
  plt.show()


def check_int_scalar(a, name):
  assert isinstance(a, int), '{} must be a int scalar, instead of {}'.format(name, type(name))


def check_callback(a, name):
  # Check http://stackoverflow.com/questions/624926/how-to-detect-whether-a-python-variable-is-a-function
  # for more details about python function type detection.
  assert callable(a), '{} must be callable, instead of {}'.format(name, type(name))


if __name__ == '__main__':
  import numpy as np

  def redraw_fn(f, axes):
    amp = float(f) / 3000
    f0 = 3
    t = np.arange(0.0, 1.0, 0.001)
    s = amp * np.sin(2 * np.pi * f0 * t)
    if not redraw_fn.initialized:
      redraw_fn.l, = axes.plot(t, s, lw=2, color='red')
      redraw_fn.initialized = True
    else:
      redraw_fn.l.set_ydata(s)

  redraw_fn.initialized = False

  videofig(100, redraw_fn)
