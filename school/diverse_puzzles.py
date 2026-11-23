#!/usr/bin/env python3
"""Six original, mathematically checked, visually distinct Grade-5 puzzles.

Generates fully owned Pillow artwork, not derivative copyrighted screenshots.
Every puzzle has one computed correct answer and an explicit worked solution.
"""
import datetime as dt
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from brand_assets import font, latin_font
from font_safety import draw_mixed, mixed_width

FIRST = dt.date(2026, 11, 24)
KINDS = ("sequence", "magic_grid", "balance", "dot_pattern", "clocks", "pyramid")
PALETTES = [
    ("#071b64", "#0c74ad", "#19d9e9", "#ffe66d"),
    ("#2c125a", "#8423aa", "#e594fc", "#ffe870"),
    ("#092c3f", "#117f8b", "#51e9bd", "#ffce65"),
    ("#3c194f", "#b63778", "#ff94b3", "#fff06c"),
    ("#102855", "#3857bf", "#85bafa", "#ffdd64"),
    ("#322343", "#9c515a", "#fdba78", "#b2fbe0"),
]
W, H = 1080, 1350


def choices_for(answer, serial, spread=5):
    """Generate three distinct plausible answers and an unpredictable position."""
    spread = max(2, int(spread))
    alternatives = [answer - spread, answer, answer + spread]
    if answer <= spread:
        alternatives[0] = answer + spread * 2
    shift = (serial * 7 + 1) % 3
    options = alternatives[shift:] + alternatives[:shift]
    if len(set(options)) != 3 or any(v < 0 for v in options):
        raise ValueError("Ambiguous puzzle choices")
    return [str(x) for x in options], options.index(answer)


def make_diverse(day, variant=0):
    if isinstance(day, str):
        day = dt.date.fromisoformat(day)
    if not isinstance(day, dt.date) or variant not in (0, 1, 2):
        raise ValueError("Unsupported date or puzzle variant")
    if day < dt.date(2026, 11, 23):
        raise ValueError("Dates before the new puzzle series are not supported")
    if variant == 2:
        if day != dt.date(2026, 11, 23):
            raise ValueError("Launch of the new visual format is limited to 2026-11-23")
        index = 3  # launch with a shape/dot puzzle, not tomorrow's number sequence
        number = 31
    else:
        if day < FIRST:
            raise ValueError("Previous number-wheel posts are already archived")
        days = (day - FIRST).days
        index = (days + variant) % len(KINDS)
        number = 32 + days * 2 + variant

    serial = (day - dt.date(2026, 11, 23)).days * 37 + variant * 17 + 9
    rng = random.Random(41127 + serial * 301)
    kind = KINDS[index]
    base = {
        "grade": 5, "topic": "ශිෂ්‍යත්ව බුද්ධි පරීක්ෂණය",
        "puzzle_kind": kind, "date": day.isoformat(),
        "question_number": number,
        "variant": {0: "daily", 1: "bonus", 2: "new-style"}[variant],
        "option_labels": ["1", "2", "3"],
        "learning_notes": [
            "පළමුව රූපය හොඳින් නිරීක්ෂණය කර රටාව හඳුනාගන්න.",
            "ඔබේ නිගමනයට ගැළපෙන හේතුවක් දරුවාගේ වචනවලින් විස්තර කරවන්න.",
            "මෙය මුල් නිර්මාණ අධ්‍යාපනික අභ්‍යාසයකි; නිල ශිෂ්‍යත්ව විභාග ප්‍රශ්නයක් නොවේ."
        ],
    }

    if kind == "sequence":
        offset = rng.randint(2, 14)
        step = rng.randint(2, 5)
        # Consecutive increments grow: +step, +(step+3), +(step+6), ...
        values = [offset]
        for i in range(1, 5):
            values.append(values[-1] + step + (i-1)*3)
        answer = values[-1]
        base.update(
            q="ඉදිරියට යන අංක පෙළේ හිස්තැන පුරවන්න.",
            visual={"values": [*values[:4], "?"]},
            puzzle_display=[" → ".join(str(x) for x in values[:4]) + " → ?"],
            explanation=(
                f"වෙනස්කම්: +{step}, +{step+3}, +{step+6}, +{step+9}. "
                f"ඒ නිසා {values[3]} + {step+9} = {answer}."),
        )
        options, at = choices_for(answer, serial, 3)
    elif kind == "magic_grid":
        # Lo Shu 3×3 magic square: each row, column and diagonal totals 15.
        shift = rng.randint(2, 12)
        grid = [[8+shift, 1+shift, 6+shift],
                [3+shift, 5+shift, 7+shift],
                [4+shift, 9+shift, 2+shift]]
        row, col = 1, 1
        answer = grid[row][col]
        shown = [[str(x) for x in row_values] for row_values in grid]
        shown[row][col] = "?"
        target = 15 + 3*shift
        base.update(
            q="පේළි හා තීරු එකතුව සමානයි. ? අංකය සොයන්න.",
            visual={"grid": shown, "target": target},
            puzzle_display=[" ".join(row_values) for row_values in shown] +
                           [f"සෑම පේළියකම එකතුව: {target}"],
            explanation=(
                f"සෑම පේළියකම එකතුව {target}යි. "
                f"මැද පේළියේ {grid[1][0]} + ? + {grid[1][2]} = {target}. "
                f"ඒ නිසා ? = {target} - {grid[1][0]} - {grid[1][2]} = {answer}."),
        )
        options, at = choices_for(answer, serial, 2)
    elif kind == "balance":
        circle = rng.randint(5, 13)
        square = rng.randint(2, 8)
        first, second = 2*circle + square, circle + 2*square
        answer = circle
        base.update(
            q="රවුමක අගය කීයද? රූප දෙකම භාවිත කරන්න.",
            visual={"circle": circle, "square": square, "first": first, "second": second},
            puzzle_display=[f"රවුම + රවුම + කොටුව = {first}",
                            f"රවුම + කොටුව + කොටුව = {second}"],
            explanation=(
                f"පළමු එකතුව {first}, දෙවැනි එකතුව {second}. "
                f"දෙවැනිය පළමු එකතුවේ දෙගුණයෙන් අඩු කළ විට රවුම් තුනේ අගය "
                f"2 × {first} - {second} = {3*circle}. "
                f"එම නිසා එක රවුමක අගය {3*circle} ÷ 3 = {answer}."),
        )
        options, at = choices_for(answer, serial, 2)
    elif kind == "dot_pattern":
        # First cards visually show 2×3, 3×4, 4×5; fourth 5×6 is missing.
        start = rng.randint(1, 2)
        sizes = [(start+i, start+i+1) for i in range(4)]
        counts = [a*b for a,b in sizes]
        answer = counts[-1]
        base.update(
            q="රූප රටාවේ හතරවැනි කොටුවේ තිත් කීයක් තිබිය යුතුද?",
            visual={"sizes": sizes, "counts": [*counts[:3], "?"]},
            puzzle_display=[
                f"රූප {i+1}: {a} පේළි × {b} තීරු = " +
                (str(counts[i]) if i != 3 else "?")
                for i,(a,b) in enumerate(sizes)],
            explanation=(
                f"රූප 1 සිට 3 දක්වා තිත් ගණන {counts[0]}, {counts[1]}, "
                f"{counts[2]} යි. පේළි සහ තීරු එක බැගින් වැඩි වේ. "
                f"ඊළඟට {sizes[3][0]} × {sizes[3][1]} = {answer}."),
        )
        options, at = choices_for(answer, serial, 2)
    elif kind == "clocks":
        hour = rng.randint(1, 8)
        minute = rng.choice((0, 5, 10, 15))
        start = (hour * 60 + minute) % (12*60)
        jump = rng.choice((20, 25, 35, 40))
        moments = [((start+i*jump) % (12*60)) for i in range(4)]
        answer = moments[-1]
        def clock_str(m):
            h = (m//60) % 12 or 12
            return f"{h}:{m%60:02d}"
        base.update(
            q="ඔරලෝසු වේලාවන් අතර රටාව හඳුනාගෙන අවසාන වේලාව සොයන්න.",
            visual={"minutes": [*moments[:3], None], "interval": jump},
            puzzle_display=[
                " → ".join(clock_str(m) for m in moments[:3]) + " → ?"],
            explanation=(
                f"සෑම පියවරකම විනාඩි {jump}ක් එකතු වේ. "
                f"{clock_str(moments[2])}ට විනාඩි {jump}ක් එකතු කළ විට "
                f"{clock_str(answer)} ලැබේ."),
        )
        # Clock choices should be clock strings, not raw minutes.
        other = [(answer-jump)%(12*60), answer, (answer+jump)%(12*60)]
        shift_idx = serial % 3
        other = other[shift_idx:] + other[:shift_idx]
        options = [clock_str(m) for m in other]
        at = other.index(answer)
    else:  # pyramid
        low = [rng.randint(3, 12) for _ in range(4)]
        middle = [low[i]+low[i+1] for i in range(3)]
        upper = [middle[i]+middle[i+1] for i in range(2)]
        answer = upper[0]+upper[1]
        base.update(
            q="සංඛ්‍යා පිරමිඩයේ ඉහළ හිස් ගඩොලට එන අංකය සොයන්න.",
            visual={"rows": [["?"], upper, middle, low]},
            puzzle_display=[
                "ඉහළ: ?",
                "දෙවැනි පේළිය: " + " , ".join(map(str,upper)),
                "තෙවැනි පේළිය: " + " , ".join(map(str,middle)),
                "පහළ පේළිය: " + " , ".join(map(str,low)),
            ],
            explanation=(
                "සෑම ගඩොලක්ම එයට පහළ ඇති අසල්වැසි ගඩොල් දෙකේ එකතුවයි. "
                f"දෙවැනි පේළිය {upper[0]} සහ {upper[1]}; "
                f"ඉහළ ගඩොල {upper[0]} + {upper[1]} = {answer}."),
        )
        options, at = choices_for(answer, serial, 4)

    base["choices"] = options
    base["answer"] = at
    base["correct_value"] = str(options[at])
    validate_puzzle(base)
    return base


def validate_puzzle(item):
    if item.get("puzzle_kind") not in KINDS:
        raise ValueError("Unsupported original puzzle format")
    answers = item.get("choices", [])
    at = item.get("answer")
    if (len(answers) != 3 or len(set(answers)) != 3 or
        not isinstance(at, int) or at not in range(3) or
        not item.get("explanation") or not item.get("visual") or
        not item.get("puzzle_display") or
        item.get("correct_value") != answers[at]):
        raise ValueError("Incorrect or incomplete generated puzzle")
    return True


def _base(kind):
    index = KINDS.index(kind)
    dark, lighter, highlight, accent = PALETTES[index]
    im = Image.new("RGB", (W,H), dark)
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y/(H-1)
        d.line((0,y,W,y), fill=(
            int(int(dark[1:3],16)*(1-t)+int(lighter[1:3],16)*t),
            int(int(dark[3:5],16)*(1-t)+int(lighter[3:5],16)*t),
            int(int(dark[5:7],16)*(1-t)+int(lighter[5:7],16)*t)
        ))
    haze = Image.new("RGBA",(W,H),(0,0,0,0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse((-150,450,280,970),fill=(*tuple(int(highlight[i:i+2],16) for i in (1,3,5)),55))
    hd.ellipse((850,-150,1300,340),fill=(*tuple(int(accent[i:i+2],16) for i in (1,3,5)),70))
    im = Image.alpha_composite(im.convert("RGBA"),haze.filter(ImageFilter.GaussianBlur(75))).convert("RGB")
    d = ImageDraw.Draw(im)
    for p in range(18):
        x=(p*157+79)%W
        y=(p*173+390)%H
        if 250 < y < 1000 and 80 < x < 1000:
            continue
        d.ellipse((x-3,y-3,x+3,y+3),fill=highlight)
    return im, (dark,lighter,highlight,accent)


def _sinhala(d, text, center_y, size, max_width=940, color="white"):
    while size >= 29:
        face = font(size,True)
        if mixed_width(d,text,face) <= max_width:
            x=(W-mixed_width(d,text,face))//2
            draw_mixed(d,(x,center_y),text,face,color)
            return
        size-=2
    raise ValueError("Sinhala text cannot fit in a safe font size")


def _center_num(d,text,x,y,size=65,colour="#0b2045"):
    d.text((x,y),str(text),font=latin_font(size,True),fill=colour,anchor="mm")


def _pane(d, bounds, fill="#fffef6", outline="#ffffff", radius=30, width=4):
    d.rounded_rectangle(bounds, radius=radius,fill=fill,outline=outline,width=width)


def _draw_sequence(d,v,palette):
    _,_,highlight,accent=palette
    values=v["values"]
    for i, value in enumerate(values):
        x=90+i*184
        y=470+((i%2)*62)
        _pane(d,(x,y,x+153,y+157),fill=accent if value=="?" else "#f5faff")
        _center_num(d,value,x+76,y+78,78 if value=="?" else 66)
        if i<4:
            _center_num(d,">",x+171,y+78,36,highlight)
    _sinhala(d,"අංක අතර වෙනස හඳුනාගන්න.",735,43,color="#ffffff")


def _draw_grid(d,v,palette):
    _,_,highlight,accent=palette
    grid=v["grid"]
    for row in range(3):
        for col in range(3):
            x=273+col*184
            y=369+row*184
            value=grid[row][col]
            _pane(d,(x,y,x+168,y+168),fill=accent if value=="?" else "#f3faff")
            _center_num(d,value,x+84,y+83,70)
    _sinhala(d,f"එකතුව = {v['target']}",980,54,color="#ffffff")


def _draw_token(d,kind,x,y,scale=1):
    r=int(36*scale)
    if kind=="circle":
        d.ellipse((x-r,y-r,x+r,y+r),fill="#ffd65a",outline="#12275e",width=5)
    else:
        d.rounded_rectangle((x-r,y-r,x+r,y+r),radius=12,fill="#6de2df",outline="#12275e",width=5)


def _draw_balance(d,v,palette):
    for idx,items in enumerate((("circle","circle","square"),
                                ("circle","square","square"))):
        y=495+idx*285
        _pane(d,(90,y-80,990,y+130),fill="#f6f8ff")
        for i, token in enumerate(items):
            _draw_token(d,token,190+i*143,y+18)
            if i < 2:
                _center_num(d,"+",261+i*143,y+18,48)
        _center_num(d,"=",665,y+18,60)
        _center_num(d,v["first"] if idx==0 else v["second"],804,y+18,69)
    _sinhala(d,"රවුමක අගය සොයන්න.",1065,42,color="#ffffff")


def _draw_dots(d,v,palette):
    _,_,highlight,accent=palette
    cards=((55,350),(558,350),(55,683),(558,683))
    for idx,(x,y) in enumerate(cards):
        _pane(d,(x,y,x+465,y+280),fill="#eef7ff")
        rows,cols=v["sizes"][idx]
        if idx==3:
            _center_num(d,"?",x+232,y+140,125)
        else:
            gap=min(40,290/max(cols,1),145/max(rows,1))
            for r in range(rows):
                for c in range(cols):
                    xx=x+232+(c-(cols-1)/2)*gap
                    yy=y+130+(r-(rows-1)/2)*gap
                    d.ellipse((xx-12,yy-12,xx+12,yy+12),fill=accent,outline="#102c65",width=2)
        _center_num(d,f"{idx+1}",x+44,y+35,32,"#273b65")


def _clock(d,cx,cy,minute_value,highlight):
    r=148
    d.ellipse((cx-r-8,cy-r-8,cx+r+8,cy+r+8),fill="#102051")
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill="#ffffff",outline=highlight,width=7)
    if minute_value is None:
        _center_num(d,"?",cx,cy,128)
        return
    hour=minute_value//60%12
    minute=minute_value%60
    for h in range(12):
        angle=math.radians(h*30-90)
        ax=cx+math.cos(angle)*116
        ay=cy+math.sin(angle)*116
        d.ellipse((ax-4,ay-4,ax+4,ay+4),fill="#2b3757")
    hangle=math.radians((hour+minute/60)*30-90)
    mangle=math.radians(minute*6-90)
    d.line((cx,cy,cx+math.cos(hangle)*76,cy+math.sin(hangle)*76),fill="#091638",width=12)
    d.line((cx,cy,cx+math.cos(mangle)*104,cy+math.sin(mangle)*104),fill="#db3673",width=7)
    d.ellipse((cx-8,cy-8,cx+8,cy+8),fill="#172c5e")


def _draw_clocks(d,v,palette):
    _,_,highlight,accent=palette
    positions=((286,503),(794,503),(286,859),(794,859))
    for (x,y), minute in zip(positions,v["minutes"]):
        _clock(d,x,y,minute,highlight)


def _draw_pyramid(d,v,palette):
    _,_,highlight,accent=palette
    for level,row in enumerate(v["rows"]):
        count=len(row)
        width=170
        step=186
        left=(W-(count*step-16))//2
        top=365+level*178
        for i,value in enumerate(row):
            x=left+i*step
            _pane(d,(x,top,x+width,top+148),fill=accent if value=="?" else "#f9f6ff")
            _center_num(d,value,x+width/2,top+72,68)


def render_diverse_poster(question,destination):
    validate_puzzle(question)
    im, palette = _base(question["puzzle_kind"])
    d=ImageDraw.Draw(im)
    _,_,highlight,accent=palette
    _pane(d,(275,24,805,99),fill="#091a55",outline=highlight)
    _sinhala(d,f"ප්‍රශ්න අංක {question['question_number']}",35,47,490)
    _sinhala(d,"5 ශ්‍රේණිය - බුද්ධි පරීක්ෂණය",144,59,1000,color=accent)
    _sinhala(d,question["q"],245,39,1010)
    kind=question["puzzle_kind"]
    renderers={
        "sequence":_draw_sequence, "magic_grid":_draw_grid,
        "balance":_draw_balance, "dot_pattern":_draw_dots,
        "clocks":_draw_clocks, "pyramid":_draw_pyramid
    }
    renderers[kind](d,question["visual"],palette)
    for i,val in enumerate(question["choices"]):
        x=55+344*i
        _pane(d,(x,1112,x+298,1180),fill="#0c1b49",outline=accent,radius=18,width=3)
        _center_num(d,f"({i+1}) {val}",x+149,1146,48,"#ffffff")
    _pane(d,(53,1210,1027,1280),fill="#0b1444",outline=accent,radius=18,width=3)
    _sinhala(d,"ඔබේ පිළිතුර කමෙන්ට් කරන්න!",1221,42,920)
    _sinhala(d,"පුංචි නැණ මඟ",1301,29,700,color="#fff1b8")
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    im.save(destination,optimize=True)
    if im.size!=(W,H) or destination.stat().st_size<20000:
        raise RuntimeError("Original Sinhala poster render failed")
    return destination
