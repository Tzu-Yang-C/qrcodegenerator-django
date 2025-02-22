from django.shortcuts import render
from django.http import HttpResponse
import qrcode
from io import BytesIO
import base64
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer, VerticalBarsDrawer,GappedSquareModuleDrawer,HorizontalBarsDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask, RadialGradiantColorMask, VerticalGradiantColorMask, HorizontalGradiantColorMask,SquareGradiantColorMask

def generate_qr(request):
    qr_code = None

    if request.method == "POST":
        version = int(request.POST.get("version", 1))
        error_correction = int(request.POST.get("error_correction", 1))
        box_size = int(request.POST.get("box_size", 10))
        border = int(request.POST.get("border", 4))
        color_a = request.POST.get("color_a", "#ffffff")  
        color_b = request.POST.get("color_b", "#0000ff")  
        data = request.POST.get("data", "https://example.com")

        error_correction_map = {
            1: qrcode.constants.ERROR_CORRECT_L,
            2: qrcode.constants.ERROR_CORRECT_M,
            3: qrcode.constants.ERROR_CORRECT_Q,
            4: qrcode.constants.ERROR_CORRECT_H,
        }

        module_drawer_map = {
            "rounded": RoundedModuleDrawer(),
            "square": SquareModuleDrawer(),
            "circle": CircleModuleDrawer(),
            "bars": VerticalBarsDrawer(),
            'GappedSquare': GappedSquareModuleDrawer(),
            'HorizontalBars': HorizontalBarsDrawer(),
        }
       
        color_a = tuple(int(color_a[i:i + 2], 16) for i in (1, 3, 5))  
        color_b = tuple(int(color_b[i:i + 2], 16) for i in (1, 3, 5))  

        color_mask_map = {
            "solid": SolidFillColorMask(color_a, color_b),
            "radial": RadialGradiantColorMask((255,255,255), color_a, color_b),
            "vertical": VerticalGradiantColorMask((255,255,255), color_a, color_b),
            "horizontal": HorizontalGradiantColorMask((255,255,255), color_a, color_b),
            "SquareGradiant": SquareGradiantColorMask((255,255,255), color_a, color_b),
        }

        module_drawer_choice = request.POST.get("module_drawer", "rounded")
        color_mask_choice = request.POST.get("color_mask", "solid")

        if request.FILES.get('logo'):
            error_correction = qrcode.constants.ERROR_CORRECT_H

        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction,  
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=module_drawer_map.get(module_drawer_choice, RoundedModuleDrawer()),
            color_mask=color_mask_map.get(color_mask_choice, SolidFillColorMask()),
        )

        if 'logo' in request.FILES:
            logo = request.FILES['logo']
            try:
                logo = Image.open(logo)
                logo = logo.convert("RGBA")  
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                logo_size = img_w // 4  
                logo = logo.resize((logo_size, logo_size))
                position = ((img_w - logo_size) // 2, (img_h - logo_size) // 2)
                
                img_with_logo = img.convert("RGBA")
                img_with_logo.paste(logo, position, logo)  
                img = img_with_logo
            except Exception as e:
                print(f"Error loading logo: {e}")
                logo = None  


        buf = BytesIO()
        img.save(buf, format="PNG")  
        qr_code = base64.b64encode(buf.getvalue()).decode('utf-8')
        print(f"QR Code Length: {len(qr_code)}") 
        print(f"Base64 QR Code (First 100 chars): {qr_code[:100]}")

    return render(request, "qrcodegenerator.html", {"qr_code": qr_code})
