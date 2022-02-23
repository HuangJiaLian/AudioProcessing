import pyaudio
import numpy as np 
from scipy import signal
import matplotlib as mpl
import matplotlib.pyplot as plt

# 转化度为弧度
def d2r(degree): return degree * np.pi / 180.

# 按下 'q' 退出程序
def on_press(event):
    global END, in_stream, p
    if event.key == 'q':
        END = True
        plt.close()
        in_stream.stop_stream()
        in_stream.close()
        p.terminate()

#================================================================
# Notes_guitar = ['E2','A2','D3','G3','B3','E4']
# 六条弦对应的音符和频率(Hz)
Notes_guitar = ['E','A','D','G','B','E'] 
freq_guitar = np.array([82.4069, 110.0000, 146.8324,\
                        195.9977, 246.9417, 329.6276])
# 表盘上显示的关键刻度
freq_ticks = np.array([0, 82.4069, 90, 110.0000, 146.8324, 180,\
                        195.9977, 246.9417, 270, 329.6276])
tick_notes = ['0 Hz','E','90','A','D','180','G','B','270','E']
#================================================================

FORMAT = pyaudio.paInt16 # 位深，16位整型表示一个采样点的值大小，
CHANNELS = 1 # 声道数目，使用单声道
# SAMPLE_RATE = 44100  # 采样率 (Hz)，每秒收集的时刻点的数目
SAMPLE_RATE = 3000  # 采样率 (Hz)，每秒收集的时刻点的数目
SAMPLE_INTERVAL = 1/SAMPLE_RATE # 采样间隔 (s), 相邻两次采样间的时间间隔
END = False # 结束标志
T = 2 # 一小段音频持续的时间 (s)
RES = 1./T # 调音器的分辨率 (Hz)，傅立叶变换后两个相邻频率点之间的频率间隔
CHUNK = T*SAMPLE_RATE # 一小段音频的采样点的数目

# 初始化麦克风输入
p = pyaudio.PyAudio()
in_stream = p.open(format=FORMAT, channels=CHANNELS, rate=SAMPLE_RATE,\
                input=True, frames_per_buffer=CHUNK)

# 作图: 参数设置
r_panel = 30 # 面板半径
pointer_len = r_panel - 1 # 指针长度
pointer_color = '#E7E0CD' # 指针颜色
pointer_width = 1 # 指针宽度
spectrum_base = 15 # 频谱图的最低位置
divide_factor = 40 # 频谱赋值缩小的倍数，目的是让图像尽量不超出面板
mpl.rcParams['toolbar'] = 'None' # 不让显示工具栏
fig = plt.figure()
plt.rcParams["font.weight"] = "bold" # 字体加粗
fig.patch.set_facecolor('#F7FBF8') # 主面板背景色
# fig.canvas.toolbar_visible = False
ax = plt.subplot(projection='polar') # 使用极坐标
ax.set_facecolor('#305996') # 调音器面板颜色设置
plt.get_current_fig_manager().set_window_title('GTuner') # 窗口名字
fig.canvas.mpl_connect('key_press_event', on_press) # 绑定按键退出的函数
# 画表盘上的主要刻度
ax.set_xticks(d2r(freq_ticks)) 
ax.set(xticklabels=tick_notes)

ax.set_ylim(0,30) # 调音面板半径的范围
# ax.set_yticks([30]) 
ax.set(yticklabels=[]) # 取消显示调音面板半径的值
ax.spines['polar'].set_color('#305996') # 调音面板外边框的颜色
ax.tick_params(axis='x', colors='#305996') # 频谱线的颜色
plt.grid()

# 表盘上的小刻度
scale = np.arange(0, 360, 10)
# 控制刻度其实位置的参数
scale_end_r = r_panel
scale_start_r = r_panel - 1
# 控制刻度宽度的参数
scale_w_min = 0.7
scale_w_max = 2.0

# 指针的起点:在中心画一个小圆圈
ax.scatter(0, 0, c=pointer_color, s=32, cmap='hsv', alpha=1) 
# 画主次要的刻度
for s in scale:
    ax.vlines(d2r(s), scale_end_r, scale_start_r, colors=pointer_color,\
              linewidth= scale_w_min, zorder=3)
# 画主要刻度
for f in freq_guitar:
    ax.vlines(d2r(f), scale_end_r, scale_start_r, colors=pointer_color,\
              linewidth= scale_w_max, zorder=3)



lowcut, highcut = 75.0, 1250.0 # 带通滤波器保留的频率范围
freq_range = [75, 350] # 吉他空弦的频率范围
freq = np.fft.rfftfreq(CHUNK, d=SAMPLE_INTERVAL) # 傅立叶变换后的横坐标
mask = (freq < freq_range[0]) + (freq > freq_range[1]) # 通过它得到吉他空弦的频率范围外的范围

mask_plot = freq < 360 # 待画的频率范围
freq_to_plot = freq[mask_plot] # 选择要画的那段频率
# 画弧度谱
line0, = ax.plot(d2r(freq_to_plot), 50*np.random.rand(len(freq_to_plot)),\
                 color=pointer_color, linewidth= pointer_width)

# 交互模式开启
plt.ion()
plt.tight_layout()
plt.show()

# 程序主体
while END==False:
    # 读取十六进制的数据到缓冲区;
    # False: 用来忽略 IOError exception    
    buffer = in_stream.read(CHUNK, exception_on_overflow = False)
    # 转化缓冲区的数据为16位的整型数据
    y = np.frombuffer(buffer, dtype = np.int16)
    # 对时域信号做傅立叶变换, 因为是输入是实数，我们使用rfft, 没有用fft。
    Y = np.fft.rfft(y)/CHUNK
    # 得到幅度谱
    Y_a = np.abs(Y)

    # 带通滤波器
    sos = signal.butter(10, [lowcut, highcut], 'bp', fs=SAMPLE_RATE, output='sos')
    filtered = signal.sosfilt(sos, y)
    FILTERED = np.fft.rfft(filtered)/CHUNK
    FILTERED_a = np.abs(FILTERED)
    
    S_a = FILTERED_a
    S_a[mask] = 0 # 强行让吉他音频范围以外的频率幅值归零
    main_freq = freq[np.argmax(S_a)] # 找到幅值最大的频率

    # 画幅度谱
    line0.set_ydata(spectrum_base+FILTERED_a[mask_plot]/divide_factor)
    # 将指针指到最大的频率位置
    vline = ax.vlines(d2r(main_freq), 0 , pointer_len, colors=pointer_color,\
                      linewidth= pointer_width, zorder=3)

    # 更新画布
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.0001)
    vline.remove() # 擦出指针旧的位置