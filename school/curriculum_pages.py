#!/usr/bin/env python3
"""Build independent grade/subject papers, answer keys, and client-side quizzes.
Original educational exercises, NOT official MoE or scholarship examination papers.
"""
import argparse
import html
import json
from pathlib import Path
from collections import Counter
from curriculum_bank import get_questions,SUBJECTS

SITE="https://gamingpoddagames.github.io/Grade-1-5-Scholarship/"
SOURCE_NOTE="2026 Grade 1 reforms and learning-area grouping: Ministry of Education and e-Thaksalawa. These are independent examples, not certified term-by-term syllabus coverage."
CSS="""
@page{size:A4;margin:18mm 16mm}
@font-face{font-family:'Sinhala';src:url('file:///usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf')}
body{font:12px/1.7 Sinhala,'DejaVu Sans',sans-serif;color:#123456}
h1{font-size:22px;color:#145f9b}h2{font-size:14px;margin:0}
.header{border-bottom:3px solid #087e76;padding-bottom:10px;margin-bottom:15px}
.small{font-size:10px;color:#53687e}
.question{break-inside:avoid;border-bottom:1px solid #d6e1e8;padding:8px 2px}
.options{padding:3px 0}.options span{display:inline-block;margin:2px 18px 2px 0}
.answer{color:#087e76;margin-top:6px}
"""
def verify(questions):
    keys=set()
    stats=Counter()
    for q in questions:
        assert q["grade"] in range(1,6),q
        assert q["subject"] in SUBJECTS,q
        assert isinstance(q["q"],str) and len(q["q"].strip())>8,q
        assert len(q["choices"])==4 and len(set(q["choices"]))==4,q
        assert isinstance(q["answer"],int) and 0<=q["answer"]<4,q
        assert q["explanation"].strip(),q
        key=(q["grade"],q["subject"],q["q"])
        assert key not in keys,("Duplicate question",key)
        keys.add(key)
        stats[(q["grade"],q["subject"])]+=1
    for grade in range(1,6):
        for subject in SUBJECTS:
            assert stats[(grade,subject)]>=8,(grade,subject,stats)
    return stats

def heading(grade,subject):
    return f"{grade} ශ්‍රේණිය – {SUBJECTS[subject]}"

def write_pdfs(root,questions):
    from weasyprint import HTML
    root.mkdir(parents=True,exist_ok=True)
    count=0
    for grade in range(1,6):
        for subject in SUBJECTS:
            rows=[q for q in questions if q["grade"]==grade and q["subject"]==subject]
            for answers in [False,True]:
                title=heading(grade,subject)+(" – පිළිතුරු" if answers else " – අභ්‍යාස ප්‍රශ්න")
                body=[f'<div class="header"><h1>{html.escape(title)}</h1><p class="small">පුංචි නැණ මඟ | මුල් නිර්මාණ අභ්‍යාස | නිල විභාග පත්‍රයක් නොවේ</p></div>']
                for ix,q in enumerate(rows,1):
                    opts="".join(f"<span>{chr(65+j)}) {html.escape(str(v))}</span>" for j,v in enumerate(q["choices"]))
                    answer=(f'<p class="answer"><b>පිළිතුර: {chr(65+q["answer"])}) {html.escape(q["choices"][q["answer"]])}</b> — {html.escape(q["explanation"])}</p>' if answers else "")
                    body.append(f'<div class="question"><h2>{ix}. {html.escape(q["q"])}</h2><div class="options">{opts}</div>{answer}</div>')
                filename=f"grade-{grade}-{subject}-"+("answers" if answers else "paper")+".pdf"
                page=f'<!doctype html><html lang="si"><meta charset="utf-8"><style>{CSS}</style><body>{"".join(body)}</body></html>'
                HTML(string=page,base_url=str(Path(__file__).parent)).write_pdf(root/filename)
                assert (root/filename).stat().st_size>1200
                count+=1
    print("Curriculum subject PDF files built:",count)

STYLES="""*{box-sizing:border-box}body{margin:0;background:#f2f8fc;color:#163554;font-family:'Noto Sans Sinhala','Nirmala UI',sans-serif;line-height:1.8}header{background:linear-gradient(110deg,#093e72,#087f78);color:white;padding:26px 16px}header .inside,main{max-width:900px;margin:auto}header a{color:#fff}h1{margin:6px 0}main{padding:18px 14px 35px}.panel{background:#fff;padding:22px;margin:16px 0;border-radius:16px;box-shadow:0 5px 20px #13385714}.links{display:flex;flex-wrap:wrap;gap:10px}a.button,button{border:0;border-radius:10px;background:#096aa6;color:white;padding:12px 15px;display:inline-block;font:inherit;text-decoration:none;cursor:pointer}a.secondary{background:#078176}.question{font-weight:700;font-size:20px}.choice{display:block;border:2px solid #d6e5ee;background:#fff;color:#183759;padding:14px;border-radius:12px;margin:9px 0;text-align:left;width:100%;cursor:pointer}.choice:hover,.choice:focus-visible{border-color:#0c83a6}.choice.chosen{background:#e5f5fc;border-color:#087c9b}.choice:disabled{cursor:default;opacity:1}.choice.correct{background:#e8f8ec;border-color:#168243}.choice.wrong{background:#fff0f0;border-color:#ce3939}.controls{display:flex;gap:10px;flex-wrap:wrap}.stats{font-weight:700;color:#086e7a}.feedback{min-height:45px}button:disabled{opacity:.55;cursor:not-allowed}.hint{font-size:13px;color:#53687e}@media(max-width:550px){.panel{padding:16px}.question{font-size:17px}}"""
QUIZ_SCRIPT=r"""
const items=window.PRACTICE_QUESTIONS;
let current=0,selected=-1,checked=false,correct=0,completed=new Set();
const $=id=>document.getElementById(id);
function view(){
  const q=items[current];selected=-1;checked=false;
  $('progress').textContent='ප්‍රශ්නය '+(current+1)+' / '+items.length+' | ලකුණු: '+correct;
  $('question').textContent=q.q;$('options').replaceChildren();
  q.choices.forEach((choice,i)=>{
    const b=document.createElement('button');b.className='choice';b.type='button';b.textContent=String.fromCharCode(65+i)+') '+choice;
    b.onclick=()=>{if(checked)return;selected=i;[...$('options').children].forEach((c,j)=>c.classList.toggle('chosen',i===j));$('check').disabled=false};
    $('options').appendChild(b);
  });
  $('feedback').textContent='පිළිතුරක් තෝරා පරීක්ෂා කරන්න.';
  $('check').disabled=true;$('next').textContent=current===items.length-1?'අවසන් ප්‍රතිඵලය':'ඊළඟ ප්‍රශ්නය';
  $('next').disabled=true;
}
$('check').onclick=()=>{
  if(selected<0||checked)return;
  checked=true;const q=items[current];
  if(selected===q.answer)correct++;
  completed.add(current);
  [...$('options').children].forEach((b,i)=>{b.disabled=true;b.classList.toggle('correct',i===q.answer);b.classList.toggle('wrong',i===selected&&i!==q.answer);});
  $('feedback').textContent=(selected===q.answer?'හරි! ':'නිවැරදි පිළිතුර: '+q.choices[q.answer]+'. ')+q.explanation;
  $('progress').textContent='ප්‍රශ්නය '+(current+1)+' / '+items.length+' | නිවැරදි: '+correct;
  $('next').disabled=false;$('check').disabled=true;
};
$('next').onclick=()=>{
  if(!checked)return;
  if(current===items.length-1){$('question').textContent='පුහුණුව අවසන්!';$('options').replaceChildren();$('feedback').textContent='ඔබ ලබාගත් ලකුණු: '+correct+' / '+items.length+'. වැරදි ප්‍රශ්න නැවත පුහුණු කරන්න.';$('check').hidden=true;$('next').hidden=true;$('restart').hidden=false;return;}
  current++;view();
};
$('restart').onclick=()=>{current=0;correct=0;completed.clear();$('restart').hidden=true;$('check').hidden=false;$('next').hidden=false;view()};
view();
"""
def write_pages(site_root,questions):
    count=0
    for grade in range(1,6):
        for subject in SUBJECTS:
            rows=[q for q in questions if q["grade"]==grade and q["subject"]==subject]
            title=heading(grade,subject)
            safe_data=json.dumps(rows,ensure_ascii=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
            pdf=f"grade-{grade}-{subject}"
            page=f"""<!doctype html><html lang="si"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} - Online Quiz සහ PDF | පුංචි නැණ මඟ</title><meta name="description" content="{html.escape(title)}. මුල් නිර්මාණ ප්‍රශ්න, පිළිතුරු, නොමිලේ PDF සහ Online Quiz."><link rel="canonical" href="{SITE}practice/grade-{grade}/{subject}/"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Sinhala:wght@400;700&display=swap"><style>{STYLES}</style></head><body><header><div class="inside"><a href="../../../">මුල් පිටුව</a> · <a href="../../../grade-{grade}/">{grade} ශ්‍රේණිය</a><h1>{html.escape(title)}</h1><p>ස්වාධීන පුහුණු ද්‍රව්‍ය — නිල විභාග පත්‍රයක් නොවේ.</p></div></header><main><div class="panel"><h2>නොමිලේ PDF</h2><div class="links"><a class="button" href="../../../downloads/{pdf}-paper.pdf" download>ප්‍රශ්න පත්‍රය PDF</a><a class="button secondary" href="../../../downloads/{pdf}-answers.pdf" download>පිළිතුරු PDF</a></div></div><section class="panel" aria-label="Online Quiz"><h2>Online Quiz</h2><p class="hint">එක් ප්‍රශ්නයකට පිළිතුරක් තෝරා පරීක්ෂා කරන්න. ප්‍රතිඵල ඔබගේ browser එක තුළ පමණක් පෙන්වයි.</p><p class="stats" id="progress"></p><p class="question" id="question"></p><div id="options"></div><p class="feedback" id="feedback" aria-live="polite"></p><div class="controls"><button id="check" disabled>පිළිතුර පරීක්ෂා කරන්න</button><button id="next" disabled>ඊළඟ ප්‍රශ්නය</button><button id="restart" hidden>නැවත ආරම්භ කරන්න</button></div></section><div class="panel"><a href="../../../">මුල් පිටුවට යන්න</a><p class="hint">මෙම අභ්‍යාස ශ්‍රී ලංකාවේ ප්‍රාථමික ඉගෙනුම් ක්ෂේත්‍ර පදනම් කර නිර්මාණය කර ඇත. පාඩම් මට්ටම් ගුරුවරයෙකුගෙන් තහවුරු කරගන්න.</p></div></main><script>window.PRACTICE_QUESTIONS={safe_data};{QUIZ_SCRIPT}</script></body></html>"""
            dest=site_root/"practice"/f"grade-{grade}"/subject
            dest.mkdir(parents=True,exist_ok=True)
            (dest/"index.html").write_text(page,encoding="utf-8")
            count+=1
    print("Subject quiz pages built:",count)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pdf-dir",required=True)
    p.add_argument("--site-dir",required=True)
    args=p.parse_args()
    questions=get_questions()
    counts=verify(questions)
    write_pdfs(Path(args.pdf_dir),questions)
    write_pages(Path(args.site_dir),questions)
    print("VALIDATED subject questions:",len(questions),dict(counts))

if __name__=="__main__":main()
