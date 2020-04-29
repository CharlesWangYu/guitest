from PIL import Image
import win32gui, win32ui, win32con, win32api

def window_capture(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if not hwnd:
        print('Window not found!')
        return 0
    # using pywin32api for the screen shot
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    if left < 0:
        return 0
    saveBitMap.CreateCompatibleBitmap(mfcDC, right - left, bottom - top)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (right - left, bottom - top) , mfcDC, (0, 0), win32con.SRCCOPY)
    # Returns the bitmap bits
    rtns = saveBitMap.GetBitmapBits(True)
    print(rtns[:20])
    bmp = Image.frombytes('RGBA', (saveBitMap.GetInfo()['bmWidth'], saveBitMap.GetInfo()['bmHeight']), rtns)
    # using pywin32api to save, what I got was a normal bitmap
    saveBitMap.SaveBitmapFile(saveDC, "a.bmp")
    # what I got was too bluish
    bmp.save("b.bmp")
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    return hwnd

window_capture('计算器')
