from display import Display
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

display = Display(rotate=90)

min_dimension = min(display.width, display.height)
top_left = (
    display.width / 2 - (min_dimension / 2 - 10),
    display.height / 2 - (min_dimension / 2 - 10),
)
bottom_right = (
    display.width / 2 + (min_dimension / 2 - 10),
    display.height / 2 + (min_dimension / 2 - 10),
)

fonts_dir = (Path(__file__).parent / "./assets/fonts").resolve()
font_regular = ImageFont.truetype(
    (fonts_dir / "Cantarell-VF.otf").resolve(),
    size=16,
)

for frame in range(360 * 4):
    image = Image.new("1", (display.width, display.height), 255)
    draw = ImageDraw.Draw(image)
    draw.arc(
        [top_left, bottom_right],
        frame * 15,
        frame * 15 + 90,
        fill=0,
        width=2,
    )
    draw.text(
        (display.width / 2, display.height / 2),
        str(frame),
        fill=0,
        font=font_regular,
        anchor="mm",
    )
    if frame == 0:
        display.display(
            image,
            update_mode=display.FULL_UPDATE,
            blocking=False,
        )
    else:
        display.display(
            image,
            update_mode=display.PARTIAL_UPDATE,
            blocking=True,
        )
