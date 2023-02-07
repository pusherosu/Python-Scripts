import win32gui
import win32con
import win32ui
import win32file
import logging
import sys
import os

from ctypes import windll
from PIL import Image

def capture_window_contents(WindowName):
	# Locate the window and assign it to a device context
	hwnd = win32gui.FindWindow(None, WindowName)
	if not hwnd:
		logging.debug("Window not found! Exiting...")
		raise Exception ("Window not found! Exiting...")

	left, top, right, bot = win32gui.GetClientRect(hwnd)
	w = right - left
	h = bot - top

	hwndDC = win32gui.GetWindowDC(hwnd)
	mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
	
	# Create a compatible save DC and create a bitmap in memory
	saveDC = mfcDC.CreateCompatibleDC()
	saveBitMap = win32ui.CreateBitmap()
	saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
	saveDC.SelectObject(saveBitMap)
	result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)

	# Build an image from memory 
	bmpinfo = saveBitMap.GetInfo()
	bmpstr = saveBitMap.GetBitmapBits(True)
	im = Image.frombuffer(
		'RGB',
		(bmpinfo['bmWidth'], bmpinfo['bmHeight']),
		bmpstr, 'raw', 'BGRX', 0, 1)

	# Release memory and device context
	win32gui.DeleteObject(saveBitMap.GetHandle())
	saveDC.DeleteDC()
	mfcDC.DeleteDC()
	win32gui.ReleaseDC(hwnd, hwndDC)

	if result == 1:
		im.save(FilePath)
	else:
		logging.debug("Document could not be saved!")
		raise Exception ("Document could not be saved!")
