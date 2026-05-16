import sys
import numpy as np

sbox = open("sbox", "rb").read()

def interleave(a, b, c):
	res = b""
	for i in range(max(len(a), len(b), len(c))):
		res += a[i:i+1]
		res += b[i:i+1]
		res += c[i:i+1]
	return res

def encrypt(package_name, device_name, version):
	a = package_name
	b = device_name

	x = interleave(device_name[::-1], package_name[::-1], version[::-1])

	x = b"%04d" % x[-1] + x

	chksum = 1 + sum(b)
	chksum += sum(a)

	iv = (len(x) + chksum) % 10

	res = ""
	for i in range(len(x)):
		sel = (iv + i) % 10
		s = sbox[sel*97:(sel+1)*97]
		res += chr(s[x[i]-32])
	return res

pattern_name = sys.argv[1].encode('ascii')
data = np.fromfile(sys.argv[2], "<f")
data = data[:50000000]

sample_rate = 20e6
bandwidth = 20000000

open(pattern_name.decode('ascii') + ".wvi", "w").write(f"""[Header]
Product Name =Anritsu
Soft Type =MX3700
File Type =WAVEDATA
Option File01 =*.wvd

[Comment]

[Wave Info]
;IQproducer Version 5.00
Use Option File = *.wvd
Note = Convert_IQproducer
Version = 1.00
Enciphered Version = {encrypt(pattern_name, b"MG3700", b"1.00")}
License Name = STANDARD
Enciphered License Name = "{encrypt(pattern_name, b"MG3700", b"STANDARD")}"
Package = DVB
Enciphered Package = "{encrypt(pattern_name, b"MG3700", b"DVB")}"
Pattern Name = {pattern_name.decode('ascii')}
Sampling Rate = {sample_rate}Hz
RMS Value = 1634
Peak Power = 2311
SM Filter = Auto
Spectrum = Normal
Over Sampling = 1
Interpolation = AUTO
Bandwidth = {bandwidth}Hz
System Unit = sample
Data Points = {len(data)//2}
Frame Length = 1000
Gap Length = 0
Freq Offset = 0Hz
AWGN Conversion Value = 0.00dB
Freq Switching Speed = Normal
Internal FIR = Off
Data Width = 16
""")

print(np.min(data), np.max(data))

rms = np.sqrt(np.mean(data**2))

data *= 1634 / rms

print("rms now", np.sqrt(np.mean(data**2)))

print(np.min(data), np.max(data))
data += 0x2000
data = np.round(data)
data = data.astype(">H")
data ^= 0x2000
print(np.min(data), np.max(data))

data = data.reshape(-1, 2)
data[:,1] |= 0x4000
data = data.flatten()
print(data)

data.astype(">H").tofile(pattern_name.decode('ascii') + ".wvd")
