
import pyaudio # 收集声音
import numpy as np # 处理声音数据
import matplotlib.pyplot as plt # 作图
import matplotlib as mpl 
from numpy.fft import rfft, rfftfreq # 傅立叶变换

# 输入音频参数设置
END = False
audio_fmt = pyaudio.paInt8
channel_num = 1
sample_rate = 2200
sample_interval = 1/sample_rate
sample_time = 0.1 # 1/10 秒保证实时效果
chunk = int(sample_time/sample_interval)
p = pyaudio.PyAudio()
stream = p.open(format=audio_fmt, channels=channel_num, rate=sample_rate,\
                input=True, frames_per_buffer=chunk)

# 按键中断: 按下按键执行该函数
def on_press(event):
    global stream, p, END
    if event.key == 'q':
        plt.close()
        stream.stop_stream()
        stream.close()
        p.terminate()
        END = True

# 作图的设置
mpl.rcParams['toolbar'] = 'None' # 不展示工具栏
fig, ax = plt.subplots(figsize=(12,3))
fig.canvas.mpl_connect('key_press_event', on_press) # 连接一个按键中断函数
plt.subplots_adjust(left=0.001, top=0.999,right=0.999,bottom=0.001) # 设置边距
plt.get_current_fig_manager().set_window_title('Spectrum') # 设置窗口名字
freq = rfftfreq(chunk, d=sample_interval) # 得到傅立叶变换的横坐标
y_data= np.random.rand(freq.size) 
line, = ax.step(freq, y_data, where='mid', color='#C04851') 
ax.set_xlim(80,1100) # 人声的大概频率范围
ax.set_ylim(-5,5)
plt.axis('off') # 关掉坐标
plt.ion() # 交互模式打开，可动态刷新图像
plt.show()

# 程序主体
while END==False:
    data = stream.read(chunk, exception_on_overflow=False) # 获取数据
    data = np.frombuffer(data, dtype=np.int8) # 将16进制的数据转化成8位整型
    X = rfft(data) # 对实数序列做傅立叶变换
    y_data = np.abs(X)*0.01 # 得到幅度, 适当缩放
    line.set_ydata(y_data) # 更新y坐标数据
    axfill = ax.fill_between(freq, 0,  y_data, step="mid",
                             color='#C04851', alpha =0.7)
    axfill_ = ax.fill_between(freq, 0,  -1*y_data, step="mid",
                             color='#C04851', alpha =0.075)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.01)
    axfill.remove() # 删除填充的区域
    axfill_.remove()