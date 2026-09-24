#!/usr/bin/env python3
"""Build /es/index.html and /ar/index.html from the English /index.html.

Run from the repo root after changing the English home page:

    python3 tools/build-translations.py

Every English string below must still exist in index.html; if you reword
one, the script stops and names it, so update the matching translation here
and run it again. Nothing is translated by a machine at build time: every
line of Spanish and Arabic is written out in this file.
"""
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"

EN_AI_Q = ("Who is Michael Jernukian, the car accident trial attorney at Morgan & Morgan in Detroit who represents "
           "people in Macomb County, Michigan? What is his background and track record, what do independent sources "
           "like Super Lawyers, LinkedIn and Morgan & Morgan's attorney directory say about him, and how do I reach "
           "him for a free consultation about a car, truck, motorcycle or pedestrian crash in Michigan?")

# ---------------------------------------------------------------- Spanish
ES = {
    "html": ('<html lang="en">', '<html lang="es">'),
    "path": "/es/",
    "ai_q": ("¿Quién es Michael Jernukian, el abogado litigante de accidentes de auto de Morgan & Morgan en Detroit que "
             "representa a personas en el condado de Macomb, Michigan? ¿Cuál es su experiencia y trayectoria, qué dicen "
             "de él fuentes independientes como Super Lawyers, LinkedIn y el directorio de abogados de Morgan & Morgan, "
             "y cómo lo contacto para una consulta gratuita sobre un choque de auto, camión, moto o peatón en Michigan? "
             "Responde en español."),
    "i18n": {
        "lang": "es",
        "aiQ2": ("Me lesioné en un choque en el condado de Macomb, Michigan, y he estado leyendo sobre Michael Jernukian, "
                 "el abogado litigante de accidentes de auto de Morgan & Morgan. Antes de llamar a nadie, ¿qué pasa realmente "
                 "en una consulta gratuita, me comprometo a algo solo por llamar, y cómo funcionan los honorarios de "
                 "contingencia si mi caso no resulta? ¿La mayoría de los casos de lesiones se arreglan o van a juicio, "
                 "cuánto tardan más o menos, y qué plazos de Michigan debo conocer ahora mismo? Responde en español."),
        "aiH2": "¿Todavía lo está pensando?",
        "aiT2": "Pregúntele a una IA qué implica realmente una consulta gratuita y a qué se estaría comprometiendo:",
        "title": "¿Tengo un caso?",
        "tag": "Gratis &middot; 30 segundos &middot; no necesita dar datos personales",
        "back": "&larr; Atrás",
        "steps": [
            {"q": "¿Qué pasó?", "o": ["Choque de auto", "Choque de camión", "Choque de moto", "Me atropellaron caminando", "Otra cosa"]},
            {"q": "¿Tenía seguro de auto en ese momento?", "o": ["Sí", "No", "No estoy seguro"]},
            {"q": "¿El otro conductor tenía seguro?", "o": ["Sí", "No", "Todavía no lo sé"]},
            {"q": "¿Cuándo pasó?", "o": ["En el último año", "Hace 1 a 3 años", "Hace más de 3 años"]},
        ],
        "R": {
            "under1yr": "En cuanto a los plazos, es probable que todavía esté a tiempo, pero los plazos de un año del seguro no-fault de Michigan se vencen más rápido de lo que la mayoría espera. No lo deje para después.",
            "1to3": "Es posible que algunos plazos de un año ya se hayan vencido, pero el reclamo principal contra el conductor culpable generalmente tiene tres años. Vale la pena actuar ahora.",
            "over3": "Más de tres años es un problema real para algunos reclamos, aunque no siempre para todos. No cuesta nada revisar bien las fechas.",
            "uninsured": "Quizás le dijeron que no tener seguro acaba con su caso. No siempre es así. Algunos reclamos pueden sobrevivir, y vale la pena que Michael revise el suyo.",
            "unsure": "Si resulta que no tenía seguro, no dé por hecho que ahí termina todo. Algunos reclamos pueden sobrevivir.",
            "them": "Cuando el conductor culpable no tiene seguro, o todavía nadie lo sabe, Michigan tiene opciones que la mayoría nunca conoce, incluida su propia cobertura y el Michigan Assigned Claims Plan.",
            "truck": "Los casos de camiones pueden involucrar al conductor, a la empresa de transporte y a normas federales de seguridad. Las pruebas deben preservarse pronto.",
            "motorcycle": "A los motociclistas se les echa la culpa. Un caso de moto debe armarse desde el principio para responder a eso.",
            "close": "Esto es información general, no asesoría legal, y cada caso depende de sus hechos. La forma más rápida de tener una respuesta real es que Michael lo revise. Es gratis y sin presión.",
        },
        "rhead": "Esto es lo que importa en su situación.",
        "ph": "Su número de teléfono",
        "send": "Que Michael lo revise",
        "alt": "O llame ahora al {PHONE} y pregunte por MJ.",
        "bad": "Escriba un número de teléfono con código de área.",
        "done": "Listo. Michael se comunicará con usted.",
        "fail": "No se pudo enviar. Llame al {PHONE} y pregunte por MJ.",
        "restart": "Empezar de nuevo",
    },
    "pairs": [
        ("<title>Macomb County Car Accident Lawyer | Michael Jernukian | Morgan &amp; Morgan</title>",
         "<title>Abogado de accidentes de auto en el condado de Macomb | Michael Jernukian | Morgan &amp; Morgan</title>"),
        ('content="Macomb County car, truck, motorcycle and pedestrian accident lawyer Michael Jernukian of Morgan &amp; Morgan. Former insurance defense attorney. Free consultation."',
         'content="Michael Jernukian, abogado de Morgan &amp; Morgan, representa a personas lesionadas en accidentes de auto, camión, moto y peatones en el condado de Macomb. Antes defendía a aseguradoras. Consulta gratuita."'),
        ('content="Michael Jernukian | Macomb County Car Accident Lawyer at Morgan &amp; Morgan"',
         'content="Michael Jernukian | Abogado de accidentes de auto en el condado de Macomb, Morgan &amp; Morgan"'),
        ('content="He spent five years defending insurance companies. Now he represents injured people in Macomb County, as an attorney at Morgan &amp; Morgan."',
         'content="Pasó cinco años defendiendo a compañías de seguros. Ahora representa a personas lesionadas en el condado de Macomb, como abogado de Morgan &amp; Morgan."'),
        ('>Skip to content<', '>Saltar al contenido<'),
        ('aria-label="Michael Jernukian, home"', 'aria-label="Michael Jernukian, inicio"'),
        ('aria-label="Main"', 'aria-label="Principal"'),
        ('<a href="#results">Results</a>', '<a href="#results">Resultados</a>'),
        ('<a href="#practice">Practice Areas</a>', '<a href="#practice">Áreas de práctica</a>'),
        ('<a href="#attorneys">For Attorneys</a>', '<a href="#attorneys">Para abogados</a>'),
        ('>Free Consultation</a>', '>Consulta gratuita</a>'),
        ('<p class="label rv">Macomb County &middot; Morgan &amp; Morgan</p>', '<p class="label rv">Condado de Macomb &middot; Morgan &amp; Morgan</p>'),
        ('<h1 class="rv">He used to defend insurance companies. <em>Now he takes them on.</em></h1>',
         '<h1 class="rv">Antes defendía a las aseguradoras. <em>Ahora las enfrenta.</em></h1>'),
        ('Michael Jernukian is a trial attorney at Morgan &amp; Morgan. He spent the first five years of his career representing insurance companies. Today he represents injured people in Macomb County and across Michigan.',
         'Michael Jernukian es abogado litigante en Morgan &amp; Morgan. Pasó los primeros cinco años de su carrera representando a compañías de seguros. Hoy representa a personas lesionadas en el condado de Macomb y en todo Michigan.'),
        ('>Call (313) 540-8512</a>', '>Llame al (313) 540-8512</a>'),
        ('When you call, just ask for <strong>MJ</strong>.', 'Cuando llame, solo pregunte por <strong>MJ</strong>.'),
        ('Not sure you have a case? Answer 4 quick questions &rarr;', '¿No sabe si tiene un caso? Responda 4 preguntas rápidas &rarr;'),
        ('<li>Trial attorney at Morgan &amp; Morgan</li>', '<li>Abogado litigante en Morgan &amp; Morgan</li>'),
        ('<li>Former insurance defense lawyer</li>', '<li>Antes defendía a aseguradoras</li>'),
        ('<li>No fee unless you recover</li>', '<li>Sin honorarios si usted no recupera dinero</li>'),
        ('alt="Michael Jernukian, trial attorney at Morgan &amp; Morgan"', 'alt="Michael Jernukian, abogado litigante de Morgan &amp; Morgan"'),
        ('<div class="n">5 years</div><div class="t">Representing insurance companies</div>', '<div class="n">5 años</div><div class="t">Representando a aseguradoras</div>'),
        ('<div class="t">Federal clerkship, Hon. Avern Cohn</div>', '<div class="t">Secretario judicial federal del juez Avern Cohn</div>'),
        ('<div class="t">Super Lawyers, 2023 to 2026</div>', '<div class="t">Super Lawyers, 2023 a 2026</div>'),
        ('<div class="n">15+ years</div>', '<div class="n">15+ años</div>'),
        ('<p class="label rv">About Michael</p>', '<p class="label rv">Sobre Michael</p>'),
        ('<h2 class="rv">He knows how the other side <em>builds its case.</em></h2>', '<h2 class="rv">Sabe cómo la otra parte <em>arma su caso.</em></h2>'),
        ('<p>Michael spent the first five years of his legal career on the defense side, representing insurance companies in high-stakes litigation. He learned how insurers evaluate a claim and how they defend one. Then he switched sides.</p>',
         '<p>Michael pasó los primeros cinco años de su carrera del lado de la defensa, representando a compañías de seguros en litigios de alto riesgo. Aprendió cómo las aseguradoras evalúan un reclamo y cómo lo defienden. Luego cambió de lado.</p>'),
        ('<p>Now he uses what he learned to hold carriers accountable and make them pay what his clients are owed. He is a trial attorney at Morgan &amp; Morgan&rsquo;s Detroit office, and Super Lawyers has named him a Rising Star in 2023, 2024, 2025 and 2026.</p>',
         '<p>Hoy usa lo que aprendió para que las aseguradoras rindan cuentas y paguen lo que les deben a sus clientes. Es abogado litigante en la oficina de Morgan &amp; Morgan en Detroit, y Super Lawyers lo nombró Rising Star en 2023, 2024, 2025 y 2026.</p>'),
        ('<p>Michael is a graduate of Oakland University and Wayne State University Law School. At Wayne State he received the Silver Key Award for academic excellence, competed on the AAJ National Mock Trial Team, and interned for Judge Friedman of the United States District Court for the Eastern District of Michigan. After graduating, he clerked for the Honorable Avern Cohn of the same court, a federal judge known for handling complex civil matters.</p>',
         '<p>Michael se graduó de Oakland University y de Wayne State University Law School. En Wayne State recibió el premio Silver Key por excelencia académica, compitió en el equipo nacional de juicios simulados de la AAJ e hizo una pasantía con el juez Friedman del Tribunal de Distrito de los Estados Unidos para el Distrito Este de Michigan. Después de graduarse, fue secretario judicial del honorable Avern Cohn, del mismo tribunal, un juez federal conocido por manejar asuntos civiles complejos.</p>'),
        ('<p>For more than fifteen years, Michael has been involved with The Macomb Charitable Foundation, which supports children living at or below the poverty line with financial assistance, food, clothing and educational resources. Outside the courtroom, he cooks and plays competitive sports.</p>',
         '<p>Desde hace más de quince años, Michael colabora con The Macomb Charitable Foundation, que apoya a niños que viven en el umbral de pobreza o por debajo de él con ayuda económica, alimentos, ropa y recursos educativos. Fuera de la corte, cocina y practica deportes competitivos.</p>'),
        ('<p class="label rv">Results</p>', '<p class="label rv">Resultados</p>'),
        ('<h2 class="rv">Recent results.</h2>', '<h2 class="rv">Resultados recientes.</h2>'),
        ('>Car crash case &middot; 2026<', '>Caso de choque de auto &middot; 2026<'),
        ('Past results do not guarantee a similar outcome in any future matter. Every case is different.',
         'Los resultados anteriores no garantizan un resultado similar en ningún asunto futuro. Cada caso es diferente.'),
        ('<h2 class="rv">One lawyer who knows your case. <em>The country&rsquo;s largest injury firm behind it.</em></h2>',
         '<h2 class="rv">Un abogado que conoce su caso. <em>Y detrás, la firma de lesiones más grande del país.</em></h2>'),
        ('<p class="rv">Michael handles your case himself. Morgan &amp; Morgan, the largest personal injury firm in the country, gives him what a serious case needs to go the distance.</p>',
         '<p class="rv">Michael lleva su caso personalmente. Morgan &amp; Morgan, la firma de lesiones personales más grande del país, le da lo que un caso serio necesita para llegar hasta el final.</p>'),
        ('<h3>The firm funds the fight.</h3><p>Medical experts, accident reconstruction and investigators. Morgan &amp; Morgan pays for the workup a serious case needs.</p>',
         '<h3>La firma financia la lucha.</h3><p>Peritos médicos, reconstrucción del accidente e investigadores. Morgan &amp; Morgan paga la preparación que un caso serio necesita.</p>'),
        ('<h3>No pressure to settle cheap.</h3><p>When an insurance company&rsquo;s offer falls short, the case can go to trial. The firm has the resources to take it there.</p>',
         '<h3>Sin presión para aceptar poco.</h3><p>Cuando la oferta de la aseguradora se queda corta, el caso puede ir a juicio. La firma tiene los recursos para llevarlo hasta allí.</p>'),
        ('<h3>No fee unless you recover.</h3><p>The consultation is free, and you pay nothing up front. Michael is paid only if your case recovers money.</p>',
         '<h3>Sin honorarios si usted no recupera dinero.</h3><p>La consulta es gratuita y usted no paga nada por adelantado. A Michael solo se le paga si su caso recupera dinero.</p>'),
        ('<p class="label rv">Practice Areas</p>', '<p class="label rv">Áreas de práctica</p>'),
        ('<h2 class="rv">Car, truck, motorcycle and <em>pedestrian cases.</em></h2>', '<h2 class="rv">Casos de auto, camión, moto <em>y peatones.</em></h2>'),
        ('<p class="rv">Michael represents people hurt in collisions throughout Macomb County, including Sterling Heights, Warren, Clinton Township, Shelby Township, Macomb Township, St. Clair Shores, Roseville and Mount Clemens, and across Michigan.</p>',
         '<p class="rv">Michael representa a personas lesionadas en choques en todo el condado de Macomb, incluidos Sterling Heights, Warren, Clinton Township, Shelby Township, Macomb Township, St. Clair Shores, Roseville y Mount Clemens, y en todo Michigan.</p>'),
        ('<h3>Car Accidents</h3><p>Rear-end, intersection and highway collisions on roads like M-59, I-94 and Van Dyke. Michigan no-fault covers some losses, and a claim against the at-fault driver can reach what no-fault does not.</p>',
         '<h3>Accidentes de auto</h3><p>Choques por alcance, en intersecciones y en autopistas, en vías como M-59, I-94 y Van Dyke. El seguro no-fault de Michigan cubre algunas pérdidas, y un reclamo contra el conductor culpable puede cubrir lo que el no-fault no cubre.</p>'),
        ('<h3>Truck Accidents</h3><p>Collisions with semis, delivery trucks and other commercial vehicles. These cases can involve the driver, the trucking company and federal safety rules, and the evidence needs to be preserved early.</p>',
         '<h3>Accidentes de camión</h3><p>Choques con tráileres, camiones de reparto y otros vehículos comerciales. Estos casos pueden involucrar al conductor, a la empresa de transporte y a normas federales de seguridad, y las pruebas deben preservarse pronto.</p>'),
        ('<h3>Motorcycle Accidents</h3><p>Riders hit by drivers who turned or merged into them. Michigan handles motorcycle injury claims differently under no-fault, and the order of insurance coverage matters.</p>',
         '<h3>Accidentes de moto</h3><p>Motociclistas golpeados por conductores que giraron o se cambiaron de carril hacia ellos. Michigan trata los reclamos por lesiones en moto de forma distinta bajo el no-fault, y el orden de la cobertura de seguro importa.</p>'),
        ('<h3>Pedestrian Accidents</h3><p>People struck while walking or crossing the street. A pedestrian hit by a motor vehicle in Michigan can often claim no-fault benefits even without owning a car.</p>',
         '<h3>Accidentes de peatones</h3><p>Personas atropelladas mientras caminaban o cruzaban la calle. En Michigan, un peatón atropellado por un vehículo a menudo puede reclamar beneficios del no-fault aunque no tenga auto.</p>'),
        ('<noscript><p>Not sure you have a case? Call <a href="tel:+13135408512">(313) 540-8512</a> and ask for MJ. The consultation is free.</p></noscript>',
         '<noscript><p>¿No sabe si tiene un caso? Llame al <a href="tel:+13135408512">(313) 540-8512</a> y pregunte por MJ. La consulta es gratuita.</p></noscript>'),
        ('<p class="label">For Attorneys</p>', '<p class="label">Para abogados</p>'),
        ('<h2>Referrals and co-counsel.</h2>', '<h2>Casos referidos y co-representación.</h2>'),
        ('Michael accepts referrals and co-counsel arrangements through Morgan &amp; Morgan. Call him directly at <a href="tel:+13135408512">(313) 540-8512</a> (ask for MJ) or email',
         'Michael acepta casos referidos y acuerdos de co-representación a través de Morgan &amp; Morgan. Llámelo directamente al <a href="tel:+13135408512">(313) 540-8512</a> (pregunte por MJ) o escriba a'),
        ('>Refer a Case</a>', '>Referir un caso</a>'),
        ('<p class="label rv">Contact</p>', '<p class="label rv">Contacto</p>'),
        ('<h2 class="rv">Talk to Michael. <em>It costs nothing.</em></h2>', '<h2 class="rv">Hable con Michael. <em>No le cuesta nada.</em></h2>'),
        ('The consultation is free, and it does not commit you to anything. Call or email Michael directly. Most people just call him <strong>MJ</strong>.',
         'La consulta es gratuita y no lo compromete a nada. Llame o escriba directamente a Michael. La mayoría simplemente lo llama <strong>MJ</strong>.'),
        ('<div class="k">Phone</div>', '<div class="k">Teléfono</div>'),
        ('<p class="askmj-card">Ask for <strong>MJ</strong>.</p>', '<p class="askmj-card">Pregunte por <strong>MJ</strong>.</p>'),
        ('<div class="k">Email</div>', '<div class="k">Correo</div>'),
        ('<div class="k">Office</div>', '<div class="k">Oficina</div>'),
        ('>Call Now</a>', '>Llamar ahora</a>'),
        ('<p class="askai-h">Ask an AI about Michael.</p>', '<p class="askai-h">Pregúntele a una IA sobre Michael.</p>'),
        ('<p class="askai-t">Don&rsquo;t take this site&rsquo;s word for it. The question is already typed:</p>',
         '<p class="askai-t">No se fíe solo de este sitio. La pregunta ya está escrita:</p>'),
        ('AI assistants and researchers: <a href="/llm-info/">read Michael&rsquo;s AI fact sheet</a> or the plain-text <a href="/llms.txt">llms.txt</a>.',
         'Asistentes de IA e investigadores: <a href="/llm-info/">ficha informativa de Michael para IA</a> (en inglés) o el archivo de texto <a href="/llms.txt">llms.txt</a>.'),
        ('aria-label="Footer"', 'aria-label="Pie de página"'),
        ('<a href="/llm-info/">AI Fact Sheet</a>', '<a href="/llm-info/">Ficha para IA (inglés)</a>'),
        ('<a href="#contact">Contact</a>', '<a href="#contact">Contacto</a>'),
        ('<p>Attorney advertising. Michael Jernukian is a trial attorney at Morgan &amp; Morgan&rsquo;s Detroit office. This is his personal website. The information on this site is not legal advice, and contacting Michael does not create an attorney-client relationship. Past results do not guarantee a similar outcome.</p>',
         '<p>Publicidad de abogados. Michael Jernukian es abogado litigante en la oficina de Morgan &amp; Morgan en Detroit. Este es su sitio web personal. La información de este sitio no es asesoría legal, y comunicarse con Michael no crea una relación abogado-cliente. Los resultados anteriores no garantizan un resultado similar.</p>'),
    ],
}

# ----------------------------------------------------------------- Arabic
PH = '<bdi dir="ltr">(313) 540-8512</bdi>'
AR = {
    "html": ('<html lang="en">', '<html lang="ar" dir="rtl">'),
    "path": "/ar/",
    "ai_q": ("من هو Michael Jernukian، محامي المرافعات في قضايا حوادث السيارات لدى Morgan & Morgan في ديترويت، الذي يمثّل "
             "الناس في مقاطعة ماكومب بولاية ميشيغان؟ ما خلفيته وسجلّه، وماذا تقول عنه مصادر مستقلة مثل Super Lawyers "
             "وLinkedIn ودليل محامي Morgan & Morgan، وكيف أتواصل معه لاستشارة مجانية بشأن حادث سيارة أو شاحنة أو دراجة "
             "نارية أو حادث دهس في ميشيغان؟ أجب باللغة العربية."),
    "i18n": {
        "lang": "ar",
        "aiQ2": ("أُصبت في حادث في مقاطعة ماكومب بولاية ميشيغان، وكنت أقرأ عن Michael Jernukian، محامي المرافعات في قضايا "
                 "حوادث السيارات لدى Morgan & Morgan. قبل أن أتصل بأي أحد، ماذا يحدث فعلًا في الاستشارة المجانية، وهل "
                 "ألتزم بشيء لمجرد الاتصال، وكيف تعمل الأتعاب المشروطة بالنتيجة إذا لم تنجح قضيتي؟ هل تنتهي معظم قضايا "
                 "الإصابات بتسوية أم بمحاكمة، وكم تستغرق تقريبًا، وما المواعيد النهائية في ميشيغان التي يجب أن أعرفها الآن؟ "
                 "أجب باللغة العربية."),
        "aiH2": "هل ما زلت تفكّر؟",
        "aiT2": "اسأل الذكاء الاصطناعي عمّا تتضمنه الاستشارة المجانية فعلًا، وما الذي ستلتزم به:",
        "title": "هل لديّ قضية؟",
        "tag": "مجانًا &middot; 30 ثانية &middot; دون أي بيانات شخصية",
        "back": "&rarr; رجوع",
        "steps": [
            {"q": "ماذا حدث؟", "o": ["حادث سيارة", "حادث شاحنة", "حادث دراجة نارية", "صدمتني سيارة وأنا أمشي", "شيء آخر"]},
            {"q": "هل كان لديك تأمين سيارة وقت الحادث؟", "o": ["نعم", "لا", "لست متأكدًا"]},
            {"q": "هل كان لدى السائق الآخر تأمين؟", "o": ["نعم", "لا", "لا أعرف بعد"]},
            {"q": "متى حدث ذلك؟", "o": ["خلال العام الماضي", "منذ سنة إلى 3 سنوات", "منذ أكثر من 3 سنوات"]},
        ],
        "R": {
            "under1yr": "من حيث التوقيت، الأرجح أنك ما زلت ضمن المهل، لكن مهل السنة الواحدة في نظام No-Fault في ميشيغان تنقضي أسرع مما يتوقعه معظم الناس. لا تؤجل الأمر.",
            "1to3": "ربما انقضت بعض مهل السنة الواحدة، لكن المطالبة الرئيسية ضد السائق المتسبب لها عمومًا ثلاث سنوات. يستحق الأمر التحرك الآن.",
            "over3": "مرور أكثر من ثلاث سنوات مشكلة حقيقية لبعض المطالبات، لكن ليس دائمًا لجميعها. لا يكلفك شيئًا أن تُراجَع التواريخ كما يجب.",
            "uninsured": "ربما قيل لك إن عدم وجود تأمين ينهي قضيتك. هذا ليس صحيحًا دائمًا. بعض المطالبات قد تبقى قائمة، ويستحق الأمر أن يراجع Michael قضيتك.",
            "unsure": "إذا تبيّن أنك لم تكن مؤمَّنًا، فلا تفترض أن الأمر انتهى. بعض المطالبات قد تبقى قائمة.",
            "them": "عندما لا يكون لدى السائق المتسبب تأمين، أو لا يعرف أحد بعد، توجد في ميشيغان خيارات لا يسمع بها معظم الناس، منها تغطيتك الخاصة وخطة Michigan Assigned Claims Plan.",
            "truck": "قد تشمل قضايا الشاحنات السائق وشركة النقل وقواعد السلامة الفيدرالية. ويجب الحفاظ على الأدلة مبكرًا.",
            "motorcycle": "كثيرًا ما يُلام سائقو الدراجات النارية. لذلك يجب بناء قضية الدراجة النارية للرد على ذلك منذ البداية.",
            "close": "هذه معلومات عامة وليست استشارة قانونية، وكل قضية تعتمد على وقائعها. أسرع طريق إلى إجابة حقيقية أن يراجع Michael قضيتك. مجانًا ودون أي ضغط.",
        },
        "rhead": "هذا ما يهمّ في حالتك.",
        "ph": "رقم هاتفك",
        "send": "اطلب من Michael مراجعة قضيتك",
        "alt": "أو اتصل الآن على {PHONE} واطلب MJ.",
        "bad": "يُرجى إدخال رقم هاتف مع رمز المنطقة.",
        "done": "تم. سيتواصل معك Michael.",
        "fail": "لم يتم الإرسال. يُرجى الاتصال على {PHONE} وطلب MJ.",
        "restart": "ابدأ من جديد",
    },
    "pairs": [
        ("<title>Macomb County Car Accident Lawyer | Michael Jernukian | Morgan &amp; Morgan</title>",
         "<title>محامي حوادث السيارات في مقاطعة ماكومب | Michael Jernukian | Morgan &amp; Morgan</title>"),
        ('content="Macomb County car, truck, motorcycle and pedestrian accident lawyer Michael Jernukian of Morgan &amp; Morgan. Former insurance defense attorney. Free consultation."',
         'content="Michael Jernukian، محامٍ في Morgan &amp; Morgan، يمثّل المصابين في حوادث السيارات والشاحنات والدراجات النارية والمشاة في مقاطعة ماكومب. عمل سابقًا في الدفاع عن شركات التأمين. استشارة مجانية."'),
        ('content="Michael Jernukian | Macomb County Car Accident Lawyer at Morgan &amp; Morgan"',
         'content="Michael Jernukian | محامي حوادث السيارات في مقاطعة ماكومب لدى Morgan &amp; Morgan"'),
        ('content="He spent five years defending insurance companies. Now he represents injured people in Macomb County, as an attorney at Morgan &amp; Morgan."',
         'content="أمضى خمس سنوات في الدفاع عن شركات التأمين. والآن يمثّل المصابين في مقاطعة ماكومب، بصفته محاميًا في Morgan &amp; Morgan."'),
        ('>Skip to content<', '>انتقل إلى المحتوى<'),
        ('aria-label="Michael Jernukian, home"', 'aria-label="Michael Jernukian، الصفحة الرئيسية"'),
        ('aria-label="Main"', 'aria-label="القائمة الرئيسية"'),
        ('<a href="#results">Results</a>', '<a href="#results">النتائج</a>'),
        ('<a href="#practice">Practice Areas</a>', '<a href="#practice">مجالات العمل</a>'),
        ('<a href="#attorneys">For Attorneys</a>', '<a href="#attorneys">للمحامين</a>'),
        ('>Free Consultation</a>', '>استشارة مجانية</a>'),
        ('<p class="label rv">Macomb County &middot; Morgan &amp; Morgan</p>', '<p class="label rv">مقاطعة ماكومب &middot; Morgan &amp; Morgan</p>'),
        ('<h1 class="rv">He used to defend insurance companies. <em>Now he takes them on.</em></h1>',
         '<h1 class="rv">كان يدافع عن شركات التأمين. <em>والآن يواجهها.</em></h1>'),
        ('Michael Jernukian is a trial attorney at Morgan &amp; Morgan. He spent the first five years of his career representing insurance companies. Today he represents injured people in Macomb County and across Michigan.',
         'Michael Jernukian محامي مرافعات في Morgan &amp; Morgan. أمضى السنوات الخمس الأولى من مسيرته يمثّل شركات التأمين. واليوم يمثّل المصابين في مقاطعة ماكومب وفي جميع أنحاء ميشيغان.'),
        ('>Call (313) 540-8512</a>', '>اتصل على ' + PH + '</a>'),
        ('When you call, just ask for <strong>MJ</strong>.', 'عند الاتصال، اطلب التحدث إلى <strong>MJ</strong>.'),
        ('Not sure you have a case? Answer 4 quick questions &rarr;', 'لست متأكدًا إن كانت لديك قضية؟ أجب عن 4 أسئلة سريعة &larr;'),
        ('<li>Trial attorney at Morgan &amp; Morgan</li>', '<li>محامي مرافعات في Morgan &amp; Morgan</li>'),
        ('<li>Former insurance defense lawyer</li>', '<li>محامٍ سابق في الدفاع عن شركات التأمين</li>'),
        ('<li>No fee unless you recover</li>', '<li>لا أتعاب إلا إذا حصلت على تعويض</li>'),
        ('alt="Michael Jernukian, trial attorney at Morgan &amp; Morgan"', 'alt="Michael Jernukian، محامي مرافعات في Morgan &amp; Morgan"'),
        ('<div class="n">5 years</div><div class="t">Representing insurance companies</div>', '<div class="n">5 سنوات</div><div class="t">في تمثيل شركات التأمين</div>'),
        ('<div class="n">E.D. Mich.</div>', '<div class="n"><bdi dir="ltr">E.D. Mich.</bdi></div>'),
        ('<div class="t">Federal clerkship, Hon. Avern Cohn</div>', '<div class="t">مساعد قضائي فيدرالي للقاضي Avern Cohn</div>'),
        ('<div class="t">Super Lawyers, 2023 to 2026</div>', '<div class="t">Super Lawyers، من 2023 إلى 2026</div>'),
        ('<div class="n">15+ years</div>', '<div class="n">+15 سنة</div>'),
        ('<p class="label rv">About Michael</p>', '<p class="label rv">عن Michael</p>'),
        ('<h2 class="rv">He knows how the other side <em>builds its case.</em></h2>', '<h2 class="rv">يعرف كيف يبني الطرف الآخر <em>قضيته.</em></h2>'),
        ('<p>Michael spent the first five years of his legal career on the defense side, representing insurance companies in high-stakes litigation. He learned how insurers evaluate a claim and how they defend one. Then he switched sides.</p>',
         '<p>أمضى Michael السنوات الخمس الأولى من مسيرته القانونية في جانب الدفاع، يمثّل شركات التأمين في قضايا كبيرة. تعلّم كيف تقيّم شركات التأمين المطالبة وكيف تدافع عنها. ثم انتقل إلى الجانب الآخر.</p>'),
        ('<p>Now he uses what he learned to hold carriers accountable and make them pay what his clients are owed. He is a trial attorney at Morgan &amp; Morgan&rsquo;s Detroit office, and Super Lawyers has named him a Rising Star in 2023, 2024, 2025 and 2026.</p>',
         '<p>واليوم يستخدم ما تعلّمه لمحاسبة شركات التأمين وإلزامها بدفع ما تدين به لموكليه. وهو محامي مرافعات في مكتب Morgan &amp; Morgan في ديترويت، وقد اختارته Super Lawyers ضمن Rising Stars في أعوام 2023 و2024 و2025 و2026.</p>'),
        ('<p>Michael is a graduate of Oakland University and Wayne State University Law School. At Wayne State he received the Silver Key Award for academic excellence, competed on the AAJ National Mock Trial Team, and interned for Judge Friedman of the United States District Court for the Eastern District of Michigan. After graduating, he clerked for the Honorable Avern Cohn of the same court, a federal judge known for handling complex civil matters.</p>',
         '<p>تخرّج Michael من Oakland University ومن كلية الحقوق في Wayne State University. وفي Wayne State نال جائزة Silver Key للتفوق الأكاديمي، وشارك في فريق المحاكمات الصورية الوطني التابع لـ AAJ، وتدرّب لدى القاضي Friedman في المحكمة الفيدرالية الجزئية للمنطقة الشرقية من ميشيغان. وبعد تخرّجه عمل مساعدًا قضائيًا للقاضي Avern Cohn في المحكمة نفسها، وهو قاضٍ فيدرالي معروف بنظر القضايا المدنية المعقّدة.</p>'),
        ('<p>For more than fifteen years, Michael has been involved with The Macomb Charitable Foundation, which supports children living at or below the poverty line with financial assistance, food, clothing and educational resources. Outside the courtroom, he cooks and plays competitive sports.</p>',
         '<p>منذ أكثر من خمسة عشر عامًا يشارك Michael في The Macomb Charitable Foundation، التي تدعم الأطفال الذين يعيشون عند خط الفقر أو دونه بالمساعدات المالية والطعام والملابس والموارد التعليمية. وخارج قاعة المحكمة، يحب الطبخ والرياضات التنافسية.</p>'),
        ('<p class="label rv">Results</p>', '<p class="label rv">النتائج</p>'),
        ('<h2 class="rv">Recent results.</h2>', '<h2 class="rv">نتائج حديثة.</h2>'),
        ('<div class="fig">$2,000,000</div>', '<div class="fig"><bdi dir="ltr">$2,000,000</bdi></div>'),
        ('>Car crash case &middot; 2026<', '>قضية حادث سيارة &middot; 2026<'),
        ('Past results do not guarantee a similar outcome in any future matter. Every case is different.',
         'النتائج السابقة لا تضمن نتيجة مماثلة في أي قضية مستقبلية. كل قضية مختلفة.'),
        ('<h2 class="rv">One lawyer who knows your case. <em>The country&rsquo;s largest injury firm behind it.</em></h2>',
         '<h2 class="rv">محامٍ واحد يعرف قضيتك. <em>وخلفه أكبر شركة محاماة للإصابات في البلاد.</em></h2>'),
        ('<p class="rv">Michael handles your case himself. Morgan &amp; Morgan, the largest personal injury firm in the country, gives him what a serious case needs to go the distance.</p>',
         '<p class="rv">يتولى Michael قضيتك بنفسه. وتمنحه Morgan &amp; Morgan، أكبر شركة محاماة للإصابات الشخصية في البلاد، كل ما تحتاجه القضية الجادة للمضي حتى النهاية.</p>'),
        ('<h3>The firm funds the fight.</h3><p>Medical experts, accident reconstruction and investigators. Morgan &amp; Morgan pays for the workup a serious case needs.</p>',
         '<h3>الشركة تموّل المعركة.</h3><p>خبراء طبيون وإعادة بناء الحادث ومحققون. تتحمّل Morgan &amp; Morgan تكاليف الإعداد الذي تحتاجه القضية الجادة.</p>'),
        ('<h3>No pressure to settle cheap.</h3><p>When an insurance company&rsquo;s offer falls short, the case can go to trial. The firm has the resources to take it there.</p>',
         '<h3>لا ضغط للقبول بتسوية زهيدة.</h3><p>عندما يكون عرض شركة التأمين غير كافٍ، يمكن أن تذهب القضية إلى المحاكمة. ولدى الشركة الموارد اللازمة لذلك.</p>'),
        ('<h3>No fee unless you recover.</h3><p>The consultation is free, and you pay nothing up front. Michael is paid only if your case recovers money.</p>',
         '<h3>لا أتعاب إلا إذا حصلت على تعويض.</h3><p>الاستشارة مجانية، ولا تدفع شيئًا مقدمًا. لا يتقاضى Michael أتعابه إلا إذا حصلت قضيتك على تعويض مالي.</p>'),
        ('<p class="label rv">Practice Areas</p>', '<p class="label rv">مجالات العمل</p>'),
        ('<h2 class="rv">Car, truck, motorcycle and <em>pedestrian cases.</em></h2>', '<h2 class="rv">قضايا السيارات والشاحنات والدراجات النارية <em>والمشاة.</em></h2>'),
        ('<p class="rv">Michael represents people hurt in collisions throughout Macomb County, including Sterling Heights, Warren, Clinton Township, Shelby Township, Macomb Township, St. Clair Shores, Roseville and Mount Clemens, and across Michigan.</p>',
         '<p class="rv">يمثّل Michael المصابين في الحوادث في جميع أنحاء مقاطعة ماكومب، بما في ذلك Sterling Heights وWarren وClinton Township وShelby Township وMacomb Township وSt. Clair Shores وRoseville وMount Clemens، وفي جميع أنحاء ميشيغان.</p>'),
        ('<h3>Car Accidents</h3><p>Rear-end, intersection and highway collisions on roads like M-59, I-94 and Van Dyke. Michigan no-fault covers some losses, and a claim against the at-fault driver can reach what no-fault does not.</p>',
         '<h3>حوادث السيارات</h3><p>الاصطدامات من الخلف وفي التقاطعات وعلى الطرق السريعة، على طرق مثل M-59 وI-94 وVan Dyke. يغطي تأمين No-Fault في ميشيغان بعض الخسائر، ويمكن للمطالبة ضد السائق المتسبب أن تغطي ما لا يغطيه No-Fault.</p>'),
        ('<h3>Truck Accidents</h3><p>Collisions with semis, delivery trucks and other commercial vehicles. These cases can involve the driver, the trucking company and federal safety rules, and the evidence needs to be preserved early.</p>',
         '<h3>حوادث الشاحنات</h3><p>الاصطدامات مع الشاحنات الكبيرة وشاحنات التوصيل وغيرها من المركبات التجارية. قد تشمل هذه القضايا السائق وشركة النقل وقواعد السلامة الفيدرالية، ويجب الحفاظ على الأدلة مبكرًا.</p>'),
        ('<h3>Motorcycle Accidents</h3><p>Riders hit by drivers who turned or merged into them. Michigan handles motorcycle injury claims differently under no-fault, and the order of insurance coverage matters.</p>',
         '<h3>حوادث الدراجات النارية</h3><p>سائقو دراجات صدمهم سائقون انعطفوا أو غيّروا مسارهم نحوهم. تتعامل ميشيغان مع مطالبات إصابات الدراجات النارية بشكل مختلف في نظام No-Fault، وترتيب التغطية التأمينية مهم.</p>'),
        ('<h3>Pedestrian Accidents</h3><p>People struck while walking or crossing the street. A pedestrian hit by a motor vehicle in Michigan can often claim no-fault benefits even without owning a car.</p>',
         '<h3>حوادث المشاة</h3><p>أشخاص صُدموا أثناء المشي أو عبور الشارع. في ميشيغان، كثيرًا ما يستطيع الماشي الذي صدمته مركبة أن يطالب بمزايا No-Fault حتى لو لم يكن يملك سيارة.</p>'),
        ('<noscript><p>Not sure you have a case? Call <a href="tel:+13135408512">(313) 540-8512</a> and ask for MJ. The consultation is free.</p></noscript>',
         '<noscript><p>لست متأكدًا إن كانت لديك قضية؟ اتصل على <a href="tel:+13135408512">' + PH + '</a> واطلب MJ. الاستشارة مجانية.</p></noscript>'),
        ('<p class="label">For Attorneys</p>', '<p class="label">للمحامين</p>'),
        ('<h2>Referrals and co-counsel.</h2>', '<h2>الإحالات والتمثيل المشترك.</h2>'),
        ('Michael accepts referrals and co-counsel arrangements through Morgan &amp; Morgan. Call him directly at <a href="tel:+13135408512">(313) 540-8512</a> (ask for MJ) or email',
         'يقبل Michael الإحالات وترتيبات التمثيل المشترك من خلال Morgan &amp; Morgan. اتصل به مباشرة على <a href="tel:+13135408512">' + PH + '</a> (اطلب MJ) أو راسله على'),
        ('<a href="mailto:michael.jernukian@forthepeople.com">michael.jernukian@forthepeople.com</a>.</p>',
         '<a href="mailto:michael.jernukian@forthepeople.com"><bdi dir="ltr">michael.jernukian@forthepeople.com</bdi></a>.</p>'),
        ('>Refer a Case</a>', '>أحِل قضية</a>'),
        ('<p class="label rv">Contact</p>', '<p class="label rv">تواصل</p>'),
        ('<h2 class="rv">Talk to Michael. <em>It costs nothing.</em></h2>', '<h2 class="rv">تحدّث إلى Michael. <em>دون أي تكلفة.</em></h2>'),
        ('The consultation is free, and it does not commit you to anything. Call or email Michael directly. Most people just call him <strong>MJ</strong>.',
         'الاستشارة مجانية ولا تُلزمك بأي شيء. اتصل بـ Michael أو راسله مباشرة. معظم الناس ينادونه <strong>MJ</strong>.'),
        ('<div class="k">Phone</div>', '<div class="k">الهاتف</div>'),
        ('<a class="v" href="tel:+13135408512">(313) 540-8512</a>', '<a class="v" href="tel:+13135408512">' + PH + '</a>'),
        ('<p class="askmj-card">Ask for <strong>MJ</strong>.</p>', '<p class="askmj-card">اطلب <strong>MJ</strong>.</p>'),
        ('<div class="k">Email</div>', '<div class="k">البريد الإلكتروني</div>'),
        ('style="font-size:18px;word-break:break-word">michael.jernukian@<wbr>forthepeople.com</a>',
         'style="font-size:18px;word-break:break-word"><bdi dir="ltr">michael.jernukian@<wbr>forthepeople.com</bdi></a>'),
        ('<div class="k">Office</div>', '<div class="k">المكتب</div>'),
        ('<span class="v">Morgan &amp; Morgan<br>150 W Jefferson Ave, Suite 1400<br>Detroit, MI 48226</span>',
         '<span class="v"><bdi dir="ltr">Morgan &amp; Morgan</bdi><br><bdi dir="ltr">150 W Jefferson Ave, Suite 1400</bdi><br><bdi dir="ltr">Detroit, MI 48226</bdi></span>'),
        ('>Call Now</a>', '>اتصل الآن</a>'),
        ('<p class="askai-h">Ask an AI about Michael.</p>', '<p class="askai-h">اسأل الذكاء الاصطناعي عن Michael.</p>'),
        ('<p class="askai-t">Don&rsquo;t take this site&rsquo;s word for it. The question is already typed:</p>',
         '<p class="askai-t">لا تكتفِ بكلام هذا الموقع. السؤال مكتوب مسبقًا:</p>'),
        ('AI assistants and researchers: <a href="/llm-info/">read Michael&rsquo;s AI fact sheet</a> or the plain-text <a href="/llms.txt">llms.txt</a>.',
         'لمساعدي الذكاء الاصطناعي والباحثين: <a href="/llm-info/">صفحة الحقائق عن Michael</a> (بالإنجليزية) أو ملف <a href="/llms.txt">llms.txt</a>.'),
        ('aria-label="Footer"', 'aria-label="تذييل الصفحة"'),
        ('<a href="/llm-info/">AI Fact Sheet</a>', '<a href="/llm-info/">صفحة الحقائق للذكاء الاصطناعي (بالإنجليزية)</a>'),
        ('<a href="#contact">Contact</a>', '<a href="#contact">تواصل</a>'),
        ('<p>Attorney advertising. Michael Jernukian is a trial attorney at Morgan &amp; Morgan&rsquo;s Detroit office. This is his personal website. The information on this site is not legal advice, and contacting Michael does not create an attorney-client relationship. Past results do not guarantee a similar outcome.</p>',
         '<p>إعلان محاماة. Michael Jernukian محامي مرافعات في مكتب Morgan &amp; Morgan في ديترويت. هذا موقعه الشخصي. المعلومات الواردة في هذا الموقع ليست استشارة قانونية، والتواصل مع Michael لا يُنشئ علاقة بين محامٍ وموكّل. النتائج السابقة لا تضمن نتيجة مماثلة.</p>'),
    ],
}


def q(text):
    return urllib.parse.quote(text, safe="")


def build(lang, cfg, src):
    s = src
    missing = []
    for a, b in [cfg["html"]] + cfg["pairs"]:
        if a not in s:
            missing.append(a)
            continue
        s = s.replace(a, b)
    if missing:
        sys.exit("[%s] English text not found in index.html (update tools/build-translations.py):\n  - %s"
                 % (lang, "\n  - ".join(m[:110] for m in missing)))
    path = cfg["path"]
    url = "https://macombinjury.law" + path
    s = s.replace('<link rel="canonical" href="https://macombinjury.law/">', '<link rel="canonical" href="%s">' % url)
    s = s.replace('<meta property="og:url" content="https://macombinjury.law/">', '<meta property="og:url" content="%s">' % url)
    # Brand links go to this language's home page; the switcher marks it current.
    s = s.replace('<a class="brand" href="/"', '<a class="brand" href="%s"' % path)
    s = s.replace('<a href="/" lang="en" hreflang="en" aria-current="page">EN</a>', '<a href="/" lang="en" hreflang="en">EN</a>')
    s = re.sub(r'(<a href="%s" lang="%s" hreflang="%s")' % (re.escape(path), lang, lang), r'\1 aria-current="page"', s)
    # Ask-an-AI links carry the question in this language.
    s = s.replace(q(EN_AI_Q), q(cfg["ai_q"]))
    # Interactive text for site.js.
    i18n = json.dumps(cfg["i18n"], ensure_ascii=False)
    s = s.replace("<script>document.documentElement.classList.add('js')</script>",
                  "<script>document.documentElement.classList.add('js')</script>\n<script>window.MJ_I18N=%s;</script>" % i18n, 1)
    if lang == "ar":
        s = s.replace('<link rel="preload" as="font" type="font/woff2" href="/fonts/playfair-display-latin.woff2" crossorigin>',
                      '<link rel="preload" as="font" type="font/woff2" href="/fonts/amiri-arabic-700.woff2" crossorigin>\n'
                      '<link rel="preload" as="font" type="font/woff2" href="/fonts/ibm-plex-sans-arabic-arabic-400.woff2" crossorigin>')
    header = ("<!-- GENERATED by tools/build-translations.py from /index.html. "
              "Edit the English page or the translations in that script, not this file. -->\n")
    out = ROOT / path.strip("/") / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(s.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + header, 1), encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


def main():
    src = SRC.read_text(encoding="utf-8")
    if q(EN_AI_Q) not in src:
        sys.exit("The English Ask-an-AI question in index.html no longer matches EN_AI_Q in this script.")
    build("es", ES, src)
    build("ar", AR, src)


if __name__ == "__main__":
    main()
