import * as THREE from 'three';
import { OrbitControls } from './vendor/OrbitControls.js';

/* ───────────────────────── text ───────────────────────── */
const I18N = {
  en: {
    tab_path: 'Path selector', tab_astronaut: 'Astronaut status', tab_tablet: 'Tablet view', tab_rover: 'Scout rover', tab_sources: 'Sources',
    prompt_sources: 'Where every number comes from',
    src_lead: 'Everything on these screens is either measured data from the sources below or labelled as simulated. Rover motion, the hidden obstacle, suit telemetry and the rover\'s mass, speed and battery are simulated or placeholder values.',
    src_g_terrain: 'Terrain and imagery', src_g_mission: 'Rover positions and photographs', src_g_env: 'Radiation and weather', src_g_crew: 'Crew and rover limits', src_g_method: 'Method, software and our own work', src_no_link: 'no public link',
    src_g_ai: 'Use of artificial intelligence',
    src_ai: 'AI coding assistants, including Anthropic\'s Claude, were used to write and review the code, to process the data and to search for sources. The team decided the concept, checked the outputs and is responsible for the content. No AI-generated images or video are used: every image here is a NASA or USGS product, or is drawn by code from the data.',
    intro_tag: 'A rover walks the route first. Then the astronaut does.', intro_begin: 'Begin mission planning',
    intro_foot: 'NASA Space Apps Challenge 2026 · real HiRISE, CTX and THEMIS data · rover motion simulated',
    prompt_rover: 'The rover that goes first',
    spec_title: 'Scout rover · our own design', spec_lead: 'Six driven wheels on rocker-bogie arms, a camera arm at the front.',
    spec_size: 'Width × length × height', spec_wheel: 'Wheel diameter, width', spec_clear: 'Ground clearance', spec_slope: 'Slope limit, safe limit',
    spec_note: 'Dimensions are read from the team\'s CAD model, which is what you see turning here. Mass, speed and battery are not final, so route times and energy use placeholders.',
    spec_scale: 'A 12.5 cm wheel is stopped by rocks no orbiter can see. That is why the rover goes first.',
    rail_note: 'Rover motion is simulated on real NASA terrain data.',
    prompt_choose: 'Choose a path', prompt_routes: '{target}: three routes from base',
    prompt_astronaut: 'Astronaut status', prompt_tablet: 'Astronaut tablet',
    coords_title: 'Traverse coordinates', coords_start: 'Start', coords_end: 'End',
    coords_surveyed: 'Surveyed targets', coords_go: 'Fly to site', coords_show: 'Show routes',
    msg_bad: 'Enter latitude and longitude as numbers.',
    msg_outside: 'That point is outside the 10 × 10 km mission area in Jezero crater.',
    msg_base: 'Base is fixed at the landing site in this build.',
    msg_nearest: 'Using the nearest surveyed target: {name}, {d} m from the point entered.',
    team_target: 'team target',
    layers_title: 'Data layers', layer_optical: 'Optical image (CTX)', layer_slope: 'Slope (HiRISE)',
    layer_thermal: 'Thermal inertia (THEMIS)', vertical_note: 'Relief ×2. Rover not to scale.',
    legend_slope: '10–15°   15–30°   over 30°, impassable',
    legend_thermal: 'dark: loose sand   bright: firm rock',
    back_globe: '← Mars', send_rover: 'Send rover', rover_busy: 'Rover on the way…',
    ledger_title: 'Base to {target} · {why}',
    fastest: 'Fastest', safest: 'Safest', efficient: 'Most efficient',
    n_distance: 'distance', n_steepest: 'steepest', n_over: 'over {safe}°', n_time: 'rover time', n_energy: 'energy',
    why_fast: 'Least driving time. {over} m of it is steeper than {safe}°.',
    why_fast_clean: 'Least driving time, and never steeper than {safe}°.',
    why_safe: 'Never steeper than {safe}°. {extra} m longer than the fastest.',
    why_safe_same: 'Never steeper than {safe}°, at no extra distance.',
    why_eff: 'Least battery use: keeps to firmer ground. {pct}% less energy than the fastest.',
    why_eff_same: 'Least battery use. Here it matches the fastest route.',
    assumed_note: 'Time and energy use placeholder rover numbers. Distance and slope come from the terrain data.',
    log_depart: 'Rover leaves base on the {route} route.',
    log_arrive: 'Arrived at {target}. {km} km driven, steepest slope {deg}°.',
    log_return: 'Returning to base.',
    log_obstacle: 'Obstacle ahead that the orbital map does not show.',
    log_replan: 'D* Lite repaired the route: {n} repairs in {s} s. Planning from scratch: {f} s.',
    log_home_detour: 'Back at base. Detour +{d} m, recorded for the crew.',
    log_home: 'Back at base. No obstacle met on this route.',
    vitals_title: 'Suit telemetry', simulated: 'simulated',
    v_breath: 'Breathing', v_heart: 'Heart rate', v_oxygen: 'Suit O₂ remaining', v_battery: 'Suit battery', per_min: '/min',
    v_time: 'EVA elapsed', eva_play: 'Play the walk', eva_playing: 'Walking · accelerated playback', eva_replay: 'Play the walk again',
    vitals_note: 'Oxygen and suit battery are drawn down over the 8 h suit design duration as the walk time passes. Heart rate and breathing are example values: at rest, then walking.',
    clock: 'Accelerated playback · mission time T+{h}:{m} at the placeholder rover speed',
    real_title: 'For scale: Opportunity on Mars', real_speed: 'Driving speed', real_rate: 'With hazard avoidance', real_mh: 'm/hour', real_slope: 'Slope not recommended above',
    real_note: 'At Opportunity\'s 30 m/hour, the {km} km safest route to {target} is about {h} hours of driving each way. A scout like this sets out days before the walk; the playback here is accelerated.',
    sound_on: 'Breathing sound on', sound_off: 'Breathing sound off',
    photo_credit: 'Apollo 11, AS11-40-5903. NASA.',
    forecast_title: 'Expected at end of traverse', forecast_route: '{target}, {route} route',
    f_oxygen: 'Oxygen left', f_walk: 'Round trip on foot', f_battery: 'Rover battery left', f_dose: 'Radiation dose', hours: 'h',
    verdict_ok: 'Projected O₂ reserve retained: more than {r}% left at the end.',
    verdict_risk: 'Projected O₂ reserve breached: less than {r}% left at the end.',
    forecast_note: 'Oxygen uses an 8 h suit and Apollo walking speed. Rover battery uses placeholder numbers. Radiation is the mean absorbed dose rate Curiosity measured in Gale crater, 2012 to 2026.',
    no_target: 'Choose a target in Path selector first.',
    t_title: 'Along the route', t_slope: 'Slope °', t_elev: 'Elevation m', t_ground: 'Ground (TI)',
    t_rad: 'Radiation mGy/day', t_oxy: 'Oxygen use %', t_min: 'Min', t_avg: 'Avg', t_max: 'Max',
    t_temp: 'Air temp °C', t_press: 'Pressure Pa',
    t_caption: 'Arrival point, rendered from HiRISE terrain and CTX image. No rover photo exists here.',
    t_photo: 'Photo taken here by Perseverance (Navcam), sol {sol}. {credit}',
    t_note: 'Slope, elevation and ground: along this route. Air temperature and pressure: measured in Jezero by Perseverance (MEDA), sols {a}–{b}. Radiation: {n} Curiosity RAD measurements in Gale crater, {y0}–{y1}; not Jezero.',
    t_risk: 'Risk', t_safe: 'Safe',
    r_slope: '{over} m steeper than {safe}°', r_oxygen: 'oxygen reserve not kept', r_battery: 'rover battery reserve not kept',
    r_obstacle: 'unmapped obstacle on the return leg', r_none: 'Slope, oxygen and battery are within limits.',
  },
  tr: {
    tab_path: 'Patika seçici', tab_astronaut: 'Astronot durumu', tab_tablet: 'Tablet görüntüsü', tab_rover: 'Öncü rover', tab_sources: 'Kaynakça',
    prompt_sources: 'Her sayının geldiği yer',
    src_lead: 'Bu ekranlardaki her şey ya aşağıdaki kaynaklardan gelen ölçülmüş veridir ya da benzetim olarak etiketlenmiştir. Rover hareketi, gizli engel, giysi telemetrisi ve rover\'ın kütle, hız ve batarya değerleri benzetim ya da varsayımdır.',
    src_g_terrain: 'Arazi ve görüntü', src_g_mission: 'Rover konumları ve fotoğraflar', src_g_env: 'Radyasyon ve hava', src_g_crew: 'Mürettebat ve rover sınırları', src_g_method: 'Yöntem, yazılım ve kendi işimiz', src_no_link: 'herkese açık link yok',
    src_g_ai: 'Yapay zekâ kullanımı',
    src_ai: 'Kodun yazılması ve gözden geçirilmesinde, verinin işlenmesinde ve kaynak aramada Anthropic\'in Claude\'u dahil yapay zekâ kodlama yardımcıları kullanıldı. Fikre ekip karar verdi, çıktıları ekip kontrol etti ve içerikten ekip sorumludur. Yapay zekâ ile üretilmiş görsel ya da video kullanılmadı: buradaki her görsel ya bir NASA ya da USGS ürünüdür ya da veriden kodla çizilmiştir.',
    intro_tag: 'Yolu önce rover yürür. Sonra astronot.', intro_begin: 'Görev planlamaya başla',
    intro_foot: 'NASA Space Apps Challenge 2026 · gerçek HiRISE, CTX ve THEMIS verisi · rover hareketi benzetim',
    prompt_rover: 'Yola ilk çıkan rover',
    spec_title: 'Öncü rover · kendi tasarımımız', spec_lead: 'Rocker-bogie kollarda altı tahrikli teker, önde kamera kolu.',
    spec_size: 'Genişlik × uzunluk × yükseklik', spec_wheel: 'Teker çapı, genişliği', spec_clear: 'Yerden yükseklik', spec_slope: 'Eğim sınırı, güvenli sınır',
    spec_note: 'Ölçüler ekibin CAD modelinden okundu; burada dönen model o. Kütle, hız ve batarya kesin değil, bu yüzden rota süresi ve enerjisi varsayım değerlerle hesaplanıyor.',
    spec_scale: '12,5 cm\'lik tekeri, hiçbir yörünge aracının göremediği kayalar durdurur. Rover bu yüzden önden gider.',
    rail_note: 'Rover hareketi, gerçek NASA arazi verisi üzerinde benzetimdir.',
    prompt_choose: 'Lütfen patika seçiniz', prompt_routes: '{target}: üsten üç rota',
    prompt_astronaut: 'Astronot durumu', prompt_tablet: 'Astronot tableti',
    coords_title: 'Yürüyüş koordinatları', coords_start: 'Başlangıç', coords_end: 'Bitiş',
    coords_surveyed: 'Taranmış hedefler', coords_go: 'Bölgeye git', coords_show: 'Rotaları göster',
    msg_bad: 'Enlem ve boylamı sayı olarak girin.',
    msg_outside: 'Bu nokta Jezero kraterindeki 10 × 10 km görev alanının dışında.',
    msg_base: 'Bu sürümde üs, iniş noktasında sabit.',
    msg_nearest: 'En yakın taranmış hedef kullanılıyor: {name}, girilen noktaya {d} m.',
    team_target: 'ekip hedefi',
    layers_title: 'Veri katmanları', layer_optical: 'Optik görüntü (CTX)', layer_slope: 'Eğim (HiRISE)',
    layer_thermal: 'Isıl atalet (THEMIS)', vertical_note: 'Yükseklik ×2. Rover ölçekli değil.',
    legend_slope: '10–15°   15–30°   30° üstü, geçilmez',
    legend_thermal: 'koyu: gevşek kum   açık: sert kaya',
    back_globe: '← Mars', send_rover: 'Rover\'ı gönder', rover_busy: 'Rover yolda…',
    ledger_title: 'Üsten {target} · {why}',
    fastest: 'En hızlı', safest: 'En güvenli', efficient: 'En verimli',
    n_distance: 'mesafe', n_steepest: 'en dik', n_over: '{safe}° üstü', n_time: 'rover süresi', n_energy: 'enerji',
    why_fast: 'En kısa sürüş süresi. Yolun {over} metresi {safe}°\'den dik.',
    why_fast_clean: 'En kısa sürüş süresi; hiçbir yerde {safe}°\'yi aşmıyor.',
    why_safe: 'Hiçbir yerde {safe}°\'yi aşmıyor. En hızlıdan {extra} m uzun.',
    why_safe_same: 'Hiçbir yerde {safe}°\'yi aşmıyor; ek mesafe yok.',
    why_eff: 'En az batarya: sert zemini izliyor. En hızlıdan %{pct} az enerji.',
    why_eff_same: 'En az batarya. Burada en hızlı rotayla aynı.',
    assumed_note: 'Süre ve enerji varsayım rover değerlerine dayanır. Mesafe ve eğim arazi verisinden gelir.',
    log_depart: 'Rover üsten {route} rotayla ayrıldı.',
    log_arrive: '{target} noktasına varıldı. {km} km yol, en dik eğim {deg}°.',
    log_return: 'Üsse dönülüyor.',
    log_obstacle: 'Önde, yörünge haritasında görünmeyen bir engel var.',
    log_replan: 'D* Lite rotayı onardı: {s} saniyede {n} onarım. Baştan planlama: {f} sn.',
    log_home_detour: 'Üsse dönüldü. Sapma +{d} m, mürettebat için kaydedildi.',
    log_home: 'Üsse dönüldü. Bu rotada engelle karşılaşılmadı.',
    vitals_title: 'Giysi telemetrisi', simulated: 'benzetim',
    v_breath: 'Nefes', v_heart: 'Kalp ritmi', v_oxygen: 'Kalan giysi O₂', v_battery: 'Giysi bataryası', per_min: '/dk',
    v_time: 'Geçen yürüyüş süresi', eva_play: 'Yürüyüşü oynat', eva_playing: 'Yürüyor · hızlandırılmış', eva_replay: 'Yürüyüşü yeniden oynat',
    vitals_note: 'Oksijen ve giysi bataryası, yürüyüş süresi ilerledikçe 8 saatlik giysi tasarım süresine göre azalır. Kalp ritmi ve nefes örnek değerlerdir: dinlenmede, sonra yürürken.',
    clock: 'Hızlandırılmış oynatma · görev süresi T+{h}:{m} (varsayım rover hızıyla)',
    real_title: 'Ölçek için: Mars\'ta Opportunity', real_speed: 'Sürüş hızı', real_rate: 'Engelden kaçınarak', real_mh: 'm/saat', real_slope: 'Önerilmeyen eğim',
    real_note: 'Opportunity\'nin saatte 30 metresiyle, {target} hedefine {km} km\'lik en güvenli rota tek yön yaklaşık {h} saat sürüş demek. Böyle bir öncü, yürüyüşten günler önce yola çıkar; buradaki oynatma hızlandırılmıştır.',
    sound_on: 'Nefes sesi açık', sound_off: 'Nefes sesi kapalı',
    photo_credit: 'Apollo 11, AS11-40-5903. NASA.',
    forecast_title: 'Yürüyüş sonunda beklenen', forecast_route: '{target}, {route} rota',
    f_oxygen: 'Kalan oksijen', f_walk: 'Yürüyerek gidiş dönüş', f_battery: 'Kalan rover bataryası', f_dose: 'Radyasyon dozu', hours: 'sa',
    verdict_ok: 'Öngörülen O₂ payı korunuyor: yürüyüş sonunda %{r}\'den fazlası kalıyor.',
    verdict_risk: 'Öngörülen O₂ payı aşılıyor: yürüyüş sonunda %{r}\'den azı kalıyor.',
    forecast_note: 'Oksijen 8 saatlik giysi ve Apollo yürüme hızına göre. Rover bataryası varsayım değerlerle. Radyasyon, Curiosity\'nin Gale kraterinde 2012–2026 arasında ölçtüğü ortalama soğurulan doz hızı.',
    no_target: 'Önce Patika seçici\'den bir hedef seçin.',
    t_title: 'Yol boyu değerler', t_slope: 'Eğim °', t_elev: 'Yükseklik m', t_ground: 'Zemin (IA)',
    t_rad: 'Radyasyon mGy/gün', t_oxy: 'Oksijen kullanımı %', t_min: 'Min', t_avg: 'Ort', t_max: 'Maks',
    t_temp: 'Hava sıcaklığı °C', t_press: 'Basınç Pa',
    t_caption: 'Varış noktası; HiRISE arazisi ve CTX görüntüsünden oluşturuldu. Burada rover fotoğrafı yok.',
    t_photo: 'Perseverance\'ın burada çektiği fotoğraf (Navcam), sol {sol}. {credit}',
    t_note: 'Eğim, yükseklik ve zemin: bu rota boyunca. Hava sıcaklığı ve basınç: Jezero\'da Perseverance (MEDA) ölçümü, sol {a}–{b}. Radyasyon: Gale kraterinde {n} Curiosity RAD ölçümü, {y0}–{y1}; Jezero değil.',
    t_risk: 'Risk', t_safe: 'Güvenli',
    r_slope: '{over} m yol {safe}°\'den dik', r_oxygen: 'oksijen payı korunmuyor', r_battery: 'rover batarya payı korunmuyor',
    r_obstacle: 'dönüş yolunda haritada olmayan engel', r_none: 'Eğim, oksijen ve batarya sınırlar içinde.',
  },
};
let lang = 'en';
const t = (key, vars = {}) =>
  (I18N[lang][key] ?? I18N.en[key] ?? key).replace(/\{(\w+)\}/g, (_, n) => vars[n]);
const $ = (id) => document.getElementById(id);

/* ───────────────────────── sources ───────────────────────── */
// [group, name, credit, { en, tr } use, link]
const SOURCES = [
  ['terrain', 'Mars 2020 Terrain Relative Navigation HiRISE DTM Mosaic', 'USGS Astrogeology Science Center · 1 m, resampled to 5 m',
    { en: '3D terrain, slope and every route calculation.', tr: '3B arazi, eğim ve bütün rota hesapları.' }, 'https://doi.org/10.5066/P9REJ9JN'],
  ['terrain', 'Mars 2020 Science Investigation CTX Orthomosaic', 'USGS Astrogeology Science Center · 5 m · public domain',
    { en: 'The image draped on the terrain. Single-band, tinted to Mars colours for display.', tr: 'Arazinin üstüne giydirilen görüntü. Tek bantlı; gösterim için Mars renklerine boyandı.' }, 'https://astrogeology.usgs.gov/search/map/mars_2020_science_investigation_ctx_dem_mosaic'],
  ['terrain', 'THEMIS-derived Thermal Inertia of Jezero Crater', 'Edwards, C. S. and Buz, J. (2021) · 100 m · CC BY 4.0',
    { en: 'Ground type: loose sand or firm rock. Feeds the most efficient route.', tr: 'Zemin türü: gevşek kum ya da sert kaya. En verimli rotayı besler.' }, 'https://doi.org/10.5281/zenodo.4931348'],
  ['terrain', 'Viking MDIM 2.1 colour mosaic', 'NASA Mars Trek',
    { en: 'The rotating Mars globe.', tr: 'Dönen Mars küresi.' }, 'https://trek.nasa.gov/mars/'],
  ['mission', 'Perseverance localized rover stops', 'NASA/JPL-Caltech · Mars 2020 mission',
    { en: 'Coordinates of the six science stops, and the check of our grid against 388 rover positions.', tr: 'Altı bilim durağının koordinatları ve ızgaramızın 388 rover konumuyla doğrulanması.' }, 'https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json'],
  ['mission', 'Mars 2020 raw images, Navcam', 'NASA/JPL-Caltech · sols 180, 502, 565, 652, 736, 770',
    { en: 'The arrival photographs in Tablet view.', tr: 'Tablet görüntüsündeki varış fotoğrafları.' }, 'https://mars.nasa.gov/mars2020/multimedia/raw-images/'],
  ['mission', 'Apollo 11 photograph AS11-40-5903', 'NASA · public domain',
    { en: 'The astronaut image in Astronaut status.', tr: 'Astronot durumu ekranındaki astronot görseli.' }, 'https://images.nasa.gov/details/as11-40-5903'],
  ['env', 'MSL RAD reduced data records', 'NASA PDS Planetary Plasma Interactions node · MSL-M-RAD-3-RDR-V1.0',
    { en: '328 dose-rate measurements by Curiosity in Gale crater, 2012 to 2026. Not Jezero.', tr: 'Curiosity\'nin Gale kraterinde 2012–2026 arasındaki 328 doz hızı ölçümü. Jezero değil.' }, 'https://pds-ppi.igpp.ucla.edu/data/MSL-M-RAD-3-RDR-V1.0/'],
  ['env', 'Mars\' surface radiation environment measured with Curiosity', 'Hassler, D. M., et al. (2014) · Science 343',
    { en: 'Published reference for the radiation measurements.', tr: 'Radyasyon ölçümleri için yayımlanmış başvuru kaynağı.' }, 'https://doi.org/10.1126/science.1244797'],
  ['env', 'Mars 2020 MEDA weather feed', 'NASA/JPL-Caltech/CAB · sols 1130 to 1133',
    { en: 'Air temperature and pressure measured in Jezero.', tr: 'Jezero\'da ölçülen hava sıcaklığı ve basınç.' }, 'https://mars.nasa.gov/rss/api/?feed=weather&category=mars2020&feedtype=json'],
  ['crew', 'xEMU spacesuit testing', 'NASA Technical Reports Server',
    { en: 'The 8 hour suit duration behind the oxygen check.', tr: 'Oksijen kontrolündeki 8 saatlik giysi süresi.' }, 'https://ntrs.nasa.gov/citations/20240004887'],
  ['crew', 'Apollo lunar surface consumables document', 'NASA · Apollo Lunar Surface Journal',
    { en: 'Planned walking speed of 3.3 km/h and the 20% walk-back reserve. Measured on the Moon. NASA\'s original page has moved; the link is an archived copy.', tr: '3,3 km/saat planlanan yürüme hızı ve %20 dönüş payı. Ay\'da ölçüldü. NASA\'nın özgün sayfası taşındı; link arşiv kopyasıdır.' }, 'https://web.archive.org/web/20250721201910/https://www.nasa.gov/wp-content/uploads/static/history/alsj/19790073512_1979073512.pdf'],
  ['crew', 'Mars Exploration Rover Surface Operations: Driving Opportunity at Meridiani Planum', 'Biesiadecki, J. J., et al. (2005) · NASA Jet Propulsion Laboratory',
    { en: 'A real rover for scale: 3.75 cm/s driving speed, 30 m/hour with hazard avoidance, driving above 30° not recommended.', tr: 'Ölçek için gerçek bir rover: 3,75 cm/s sürüş hızı, engelden kaçınarak saatte 30 m, 30° üstünde sürüş önerilmiyor.' }, 'https://www-robotics.jpl.nasa.gov/media/documents/biesiadecki_driving05.pdf'],
  ['crew', 'Perseverance rover components', 'NASA Science',
    { en: 'Reference for rover slope limits: 45° without tipping, drivers avoid more than 30°.', tr: 'Rover eğim sınırları için başvuru: 45° devrilmeden dayanım, sürücüler 30° üstünden kaçınır.' }, 'https://science.nasa.gov/mission/mars-2020-perseverance/rover-components/'],
  ['method', 'D* Lite', 'Koenig, S. and Likhachev, M. (2002) · AAAI Conference on Artificial Intelligence',
    { en: 'The route planner, including the repair when the rover meets an unmapped obstacle.', tr: 'Rota planlayıcı; rover haritada olmayan engelle karşılaşınca yapılan onarım dahil.' }, null],
  ['method', 'Scout rover CAD model', 'SafePath team',
    { en: 'Our own design. Dimensions are read from this model.', tr: 'Kendi tasarımımız. Ölçüler bu modelden okundu.' }, null],
  ['method', 'three.js, NumPy, SciPy, Pillow, Matplotlib, trimesh, cascadio', 'Open-source software · MIT and BSD-style licences',
    { en: '3D rendering in the browser and the data pipeline.', tr: 'Tarayıcıda 3B çizim ve veri hattı.' }, 'https://threejs.org/'],
  ['method', 'Newsreader, IBM Plex Sans, IBM Plex Mono', 'SIL Open Font License',
    { en: 'Typefaces.', tr: 'Yazı tipleri.' }, 'https://fonts.google.com/'],
];
function drawSources() {
  let html = `<p class="src-lead">${t('src_lead')}</p>`, group = '';
  for (const [g, name, credit, use, link] of SOURCES) {
    if (g !== group) { group = g; html += `<p class="eyebrow src-group">${t('src_g_' + g)}</p>`; }
    html += `<div class="src-row"><p class="src-name">${name}<small>${credit}</small></p><p class="src-use">${use[lang]}</p>` +
      (link ? `<a class="src-link" href="${link}" target="_blank" rel="noopener">${link.replace(/^https?:\/\//, '')}</a>`
            : `<span class="src-none">${t('src_no_link')}</span>`) + '</div>';
  }
  html += `<p class="eyebrow src-group">${t('src_g_ai')}</p><p class="src-ai">${t('src_ai')}</p>`;
  $('sources').innerHTML = html;
}

/* ───────────────────────── state ───────────────────────── */
const COLORS = { fastest: '#f2b33d', safest: '#5fd0b5', efficient: '#8fa8ff' };
const SIZE = 1000;   // world units across the mission area (1 unit = 10 m)
const RELIEF = 2;    // vertical exaggeration
const JEZERO = { lat: 18.47, lon: 77.41 };
const state = { view: 'path', phase: 'globe', target: null, routeId: 'safest', busy: false, clockMin: 0,
                sound: true, obstacleMet: new Set(), drive: null };
let mission, height;

/* ───────────────────────── renderer and scenes ───────────────────────── */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x07080c);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.12;
const loader = new THREE.TextureLoader();
const texture = (url) => { const tx = loader.load(url); tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = 8; return tx; };

function starField(radius, count) {
  const pos = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const v = new THREE.Vector3().randomDirection().multiplyScalar(radius);
    pos.set([v.x, v.y, v.z], i * 3);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  return new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xe9dfcf, size: 1.4, sizeAttenuation: false, transparent: true, opacity: 0.75, fog: false }));
}

// Globe
const globeScene = new THREE.Scene();
const globeCam = new THREE.PerspectiveCamera(35, 1, 0.01, 200);
globeCam.position.set(0, 0, 4.4);
const globe = new THREE.Mesh(new THREE.SphereGeometry(1, 128, 96),
  new THREE.MeshStandardMaterial({ map: texture('data/mars.jpg'), roughness: 1, metalness: 0 }));
globe.rotation.y = 2.2;
globeScene.add(globe);
globeScene.add(new THREE.Mesh(new THREE.SphereGeometry(1.035, 64, 48),
  new THREE.MeshBasicMaterial({ color: 0xc8693b, transparent: true, opacity: 0.1, side: THREE.BackSide, blending: THREE.AdditiveBlending })));
const sun = new THREE.DirectionalLight(0xfff1e0, 2.6); sun.position.set(-3, 1.4, 4); globeScene.add(sun);
globeScene.add(new THREE.AmbientLight(0x8090b0, 0.35));
const globeStars = starField(60, 2600); globeScene.add(globeStars);

function onGlobe(lat, lon) {  // matches three's sphere UV for an equirectangular map centred on 0° E
  const phi = THREE.MathUtils.degToRad(lon + 180), theta = THREE.MathUtils.degToRad(90 - lat);
  return new THREE.Vector3(-Math.cos(phi) * Math.sin(theta), Math.cos(theta), Math.sin(phi) * Math.sin(theta));
}
const siteMark = new THREE.Mesh(new THREE.RingGeometry(0.012, 0.018, 40),
  new THREE.MeshBasicMaterial({ color: 0xe9dfcf, side: THREE.DoubleSide, transparent: true }));
siteMark.position.copy(onGlobe(JEZERO.lat, JEZERO.lon).multiplyScalar(1.004));
siteMark.lookAt(siteMark.position.clone().multiplyScalar(2));
globe.add(siteMark);

// Terrain
const land = new THREE.Scene();
const landCam = new THREE.PerspectiveCamera(40, 1, 1, 9000);
landCam.position.set(120, 620, 760);
const controls = new OrbitControls(landCam, renderer.domElement);
controls.enableDamping = true; controls.maxPolarAngle = 1.46; controls.minDistance = 50; controls.maxDistance = 2400;
const roverCam = new THREE.PerspectiveCamera(68, 1, 0.5, 6000);
land.add(new THREE.HemisphereLight(0xffdcc0, 0x24140c, 0.75));
const landSun = new THREE.DirectionalLight(0xfff0dc, 3.4); landSun.position.set(-700, 360, -180); land.add(landSun);
const HAZE = new THREE.FogExp2(0x140b07, 0.00026); land.fog = HAZE;
const landStars = starField(4200, 2200); land.add(landStars);
const routeGroup = new THREE.Group(), markGroup = new THREE.Group(), extraGroup = new THREE.Group();
land.add(routeGroup, markGroup, extraGroup);
const SKY = new THREE.Color(0xc39a78), VOID = new THREE.Color(0x0a0c11);

// Rover bay: the team's CAD model on a turntable
const bay = new THREE.Scene();
const bayCam = new THREE.PerspectiveCamera(30, 1, 0.01, 80);
bayCam.position.set(1.75, 0.95, 2.25); bayCam.lookAt(0, 0.3, 0);
bay.add(new THREE.HemisphereLight(0xfff1e0, 0x1a120d, 1.1));
const key = new THREE.DirectionalLight(0xfff4e6, 2.8); key.position.set(2.2, 3, 2); bay.add(key);
const rim = new THREE.DirectionalLight(0xd2703f, 2.4); rim.position.set(-2.5, 1.2, -2.2); bay.add(rim);
const turntable = new THREE.Group(); bay.add(turntable);
const pad = new THREE.Mesh(new THREE.CircleGeometry(1.05, 96), new THREE.MeshStandardMaterial({ color: 0x241811, roughness: 1 }));
pad.rotation.x = -Math.PI / 2; bay.add(pad);
const padRing = new THREE.Mesh(new THREE.RingGeometry(1.05, 1.058, 128), new THREE.MeshBasicMaterial({ color: 0xd2703f, side: THREE.DoubleSide }));
padRing.rotation.x = -Math.PI / 2; padRing.position.y = 0.001; bay.add(padRing);
bay.add(starField(40, 1800));

const starScene = new THREE.Scene();
const loneStars = starField(60, 3200); starScene.add(loneStars);

/* ───────────────────────── terrain helpers ───────────────────────── */
function heightAt(row, col) {
  const g = mission.grid, m = g.mesh;
  const fr = Math.min(Math.max((row + 0.5) / g.shape[0] * m - 0.5, 0), m - 1);
  const fc = Math.min(Math.max((col + 0.5) / g.shape[1] * m - 0.5, 0), m - 1);
  const r0 = Math.floor(fr), c0 = Math.floor(fc), r1 = Math.min(r0 + 1, m - 1), c1 = Math.min(c0 + 1, m - 1);
  const a = fr - r0, b = fc - c0;
  const h = height[r0 * m + c0] * (1 - a) * (1 - b) + height[r0 * m + c1] * (1 - a) * b +
            height[r1 * m + c0] * a * (1 - b) + height[r1 * m + c1] * a * b;
  return (h - g.height_min_m) / 10 * RELIEF;
}
function world([row, col], lift = 0) {
  const n = mission.grid.shape[0];
  return new THREE.Vector3((col + 0.5) / n * SIZE - SIZE / 2, heightAt(row, col) + lift, (row + 0.5) / n * SIZE - SIZE / 2);
}
const toPoints = (cells, lift, step = 3) => {
  const pts = [];
  for (let i = 0; i < cells.length; i += step) pts.push(world(cells[i], lift));
  pts.push(world(cells[cells.length - 1], lift));
  return pts;
};
// Draw a tube from its start to its end over time, led by a bright point.
function reveal(mesh, color, delay, seconds) {
  mesh.geometry.setDrawRange(0, 0);
  const head = new THREE.Mesh(new THREE.SphereGeometry(4, 16, 12), new THREE.MeshBasicMaterial({ color }));
  head.renderOrder = 6; head.visible = false; mesh.parent.add(head);
  reveals.push({ mesh, head, t: -delay / seconds, seconds, total: mesh.geometry.index.count });
}
function stepReveals(dt) {
  for (let i = reveals.length - 1; i >= 0; i--) {
    const r = reveals[i]; r.t += dt / r.seconds;
    if (r.t < 0) continue;
    const k = Math.min(r.t, 1), e = k < 0.5 ? 2 * k * k : 1 - 2 * (1 - k) * (1 - k);
    r.mesh.geometry.setDrawRange(0, Math.floor(e * r.total / 3) * 3);
    r.head.visible = k < 1; r.head.position.copy(r.mesh.userData.curve.getPointAt(e));
    if (k >= 1) { r.head.removeFromParent(); reveals.splice(i, 1); }
  }
}
function tube(points, color, radius, opacity = 1) {
  const curve = new THREE.CatmullRomCurve3(points, false, 'centripetal');
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, points.length * 2, radius, 6),
    new THREE.MeshBasicMaterial({ color, transparent: opacity < 1, opacity, fog: false }));
  mesh.userData.curve = curve;
  return mesh;
}
function label(text, color = '#e9dfcf') {
  const c = document.createElement('canvas'), x = c.getContext('2d');
  x.font = '500 34px "IBM Plex Mono", monospace';
  c.width = Math.ceil(x.measureText(text).width) + 24; c.height = 52;
  x.font = '500 34px "IBM Plex Mono", monospace'; x.fillStyle = color; x.textBaseline = 'middle';
  x.shadowColor = '#000'; x.shadowBlur = 8; x.fillText(text, 12, 27);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), sizeAttenuation: false, depthTest: false }));
  s.scale.set(0.032 * c.width / c.height, 0.032, 1); s.renderOrder = 5;
  return s;
}

let overlaySlope, overlayThermal, rover, obstacle;
const ROVER_SCALE = 34;  // the real rover is 0.82 m long; drawn larger so it can be seen on a 10 km map
async function loadRover() {  // the team's CAD model, see pipeline/export_rover.py
  const buf = await fetch('assets/rover.bin').then((r) => r.arrayBuffer());
  const [nVert, nIdx] = new Uint32Array(buf, 0, 2);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(buf, 8, nVert * 3), 3));
  geo.setIndex(new THREE.BufferAttribute(new Uint32Array(buf, 8 + nVert * 12, nIdx), 1));
  geo.setAttribute('color', new THREE.BufferAttribute(new Uint8Array(buf, 8 + nVert * 12 + nIdx * 4, nVert * 3), 3, true));
  geo.computeVertexNormals();
  return new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.5, metalness: 0.3 }));
}
function buildLand() {
  const m = mission.grid.mesh;
  const geo = new THREE.PlaneGeometry(SIZE, SIZE, m - 1, m - 1);
  geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) pos.setY(i, (height[i] - mission.grid.height_min_m) / 10 * RELIEF);
  // Relief shading comes from a normal map baked from the full 5 m elevation grid.
  const normal = loader.load('data/normal.jpg'); normal.anisotropy = 8;
  // The square of terrain dissolves into space at its edges instead of ending in a hard cut.
  const c = document.createElement('canvas'); c.width = c.height = 512;
  const x = c.getContext('2d'); x.fillStyle = '#000'; x.fillRect(0, 0, 512, 512);
  x.filter = 'blur(14px)'; x.fillStyle = '#fff'; x.fillRect(30, 30, 452, 452);
  const edge = new THREE.CanvasTexture(c);
  land.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    map: texture('data/basemap.jpg'), normalMap: normal, normalMapType: THREE.ObjectSpaceNormalMap,
    alphaMap: edge, transparent: true, roughness: 0.96, metalness: 0 })));
  const overlay = (url, lift) => {
    const mesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ map: texture(url), alphaMap: edge, transparent: true, depthWrite: false }));
    mesh.position.y = lift; mesh.visible = false; land.add(mesh); return mesh;
  };
  overlayThermal = overlay('data/thermal.png', 0.5);
  overlaySlope = overlay('data/slope.png', 0.9);

  rover = new THREE.Group();
  loadRover().then((model) => {
    turntable.add(new THREE.Mesh(model.geometry, model.material));
    model.scale.setScalar(ROVER_SCALE); rover.add(model);
  });
  rover.visible = false; land.add(rover);

  const r = mission.scenario.obstacle_radius_m / 10;
  obstacle = new THREE.Group();
  const disc = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 3, 40), new THREE.MeshBasicMaterial({ color: 0xe5484d, transparent: true, opacity: 0.55 }));
  obstacle.add(disc);
  for (let i = 0; i < 22; i++) {
    const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(1.2 + Math.random() * 2.4), new THREE.MeshStandardMaterial({ color: 0x5a3a2a, roughness: 1 }));
    const a = Math.random() * 6.283, d = Math.sqrt(Math.random()) * r * 0.9;
    rock.position.set(Math.cos(a) * d, 2, Math.sin(a) * d); obstacle.add(rock);
  }
  obstacle.position.copy(world(mission.scenario.obstacle_centre, 1.5));
  obstacle.visible = false; land.add(obstacle);
}

/* ───────────────────────── routes on the map ───────────────────────── */
const route = () => state.target.routes.find((r) => r.id === state.routeId);

const reveals = [];
function drawRoutes(animate) {
  routeGroup.clear(); markGroup.clear(); extraGroup.clear(); obstacle.visible = false; rover.visible = false;
  reveals.length = 0;
  const order = { fastest: 0, efficient: 1, safest: 2 };
  for (const r of state.target.routes) {
    const on = r.id === state.routeId;
    const lift = { fastest: 3.0, efficient: 3.6, safest: 4.2 }[r.id];
    const mesh = tube(toPoints(r.cells, lift), COLORS[r.id], on ? 2.1 : 1.1, on ? 1 : 0.55);
    mesh.renderOrder = on ? 3 : 2; routeGroup.add(mesh);
    if (animate) reveal(mesh, COLORS[r.id], order[r.id] * 0.55, 1.5);
  }
  const pin = (cell, color, text) => {
    const p = world(cell);
    const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 26), new THREE.MeshBasicMaterial({ color }));
    stem.position.copy(p).y += 13; markGroup.add(stem);
    const tag = label(text, color); tag.position.copy(p).y += 34; markGroup.add(tag);
  };
  pin(mission.base.cell, '#e9dfcf', 'BASE');
  pin(state.target.cell, '#c8693b', state.target.name.toUpperCase());
}

function frameRoute() {
  const a = world(mission.base.cell), b = world(state.target.cell);
  const mid = a.clone().lerp(b, 0.5), span = Math.max(a.distanceTo(b), 160);
  controls.target.copy(mid);
  const back = Math.max(span, 360);  // long routes need more room beside the panels
  landCam.position.set(mid.x + back * 0.35, mid.y + back * 1.4, mid.z + back * 1.75);
}

/* ───────────────────────── ledger ───────────────────────── */
function drawProfile(canvas, r) {
  const w = canvas.width = canvas.clientWidth * 2, h = canvas.height = 68, x = canvas.getContext('2d');
  const s = r.profile.slope, safe = mission.grid.safe_slope_deg, top = Math.max(30, r.max_slope_deg);
  const px = (i) => i / (s.length - 1) * w, py = (v) => h - 3 - v / top * (h - 8);
  x.clearRect(0, 0, w, h);
  x.beginPath(); x.moveTo(0, h);
  s.forEach((v, i) => x.lineTo(px(i), py(v))); x.lineTo(w, h); x.closePath();
  x.fillStyle = COLORS[r.id] + '55'; x.fill();
  x.lineWidth = 2;
  for (let i = 1; i < s.length; i++) {
    x.beginPath(); x.moveTo(px(i - 1), py(s[i - 1])); x.lineTo(px(i), py(s[i]));
    x.strokeStyle = Math.max(s[i], s[i - 1]) > safe ? '#e5484d' : COLORS[r.id]; x.stroke();
  }
  x.setLineDash([6, 6]); x.strokeStyle = '#8d93a3'; x.lineWidth = 1;
  x.beginPath(); x.moveTo(0, py(safe)); x.lineTo(w, py(safe)); x.stroke(); x.setLineDash([]);
}

function whyText(r) {
  const safe = mission.grid.safe_slope_deg, fast = state.target.routes.find((q) => q.id === 'fastest');
  if (r.id === 'fastest') return r.above_safe_m ? t('why_fast', { over: r.above_safe_m, safe }) : t('why_fast_clean', { safe });
  if (r.id === 'safest') {
    const extra = r.distance_m - fast.distance_m;
    return extra > 0 ? t('why_safe', { safe, extra }) : t('why_safe_same', { safe });
  }
  const pct = (fast.rover_energy_wh - r.rover_energy_wh) / fast.rover_energy_wh * 100;
  return pct >= 0.1 ? t('why_eff', { pct: pct.toFixed(1) }) : t('why_eff_same');
}

function drawLedger(animate) {
  const tg = state.target, safe = mission.grid.safe_slope_deg, box = $('routes');
  $('ledger-title').textContent = t('ledger_title', { target: tg.name, why: tg.why });
  box.innerHTML = '';
  for (const r of tg.routes) {
    const row = document.createElement('button');
    row.className = 'route' + (r.id === state.routeId ? ' is-active' : '') + (animate ? ' is-arriving' : '');
    row.style.animationDelay = ({ fastest: 1.5, efficient: 2.05, safest: 2.6 })[r.id] + 's';
    row.style.setProperty('--c', COLORS[r.id]);
    const num = (v, unit, key, vars, assume) =>
      `<span class="num${assume ? ' assume' : ''}">${v} ${unit}<small>${t(key, vars)}</small></span>`;
    row.innerHTML = `<span class="route-name"><i></i>${t(r.id)}</span><canvas></canvas>` +
      num((r.distance_m / 1000).toFixed(2), 'km', 'n_distance') +
      num(r.max_slope_deg.toFixed(1), '°', 'n_steepest') +
      num(r.above_safe_m, 'm', 'n_over', { safe }) +
      num(Math.round(r.rover_time_min), 'min', 'n_time', {}, true) +
      num(Math.round(r.rover_energy_wh), 'Wh', 'n_energy', {}, true) +
      `<span class="why">${whyText(r)}</span>`;
    row.addEventListener('click', () => { if (!state.busy) { state.routeId = r.id; refreshTarget(false); } });
    box.appendChild(row);
    drawProfile(row.querySelector('canvas'), r);
  }
}

/* ───────────────────────── astronaut and tablet panels ───────────────────────── */
function forecast() {
  const r = route(), crew = mission.crew, rv = mission.rover;
  const oxygenLeft = (1 - r.round_trip_walk_h / crew.oxygen_h) * 100;
  const batteryLeft = (1 - r.round_trip_energy_wh / rv.battery_wh) * 100;
  return { r, oxygenLeft, batteryLeft, oxygenUse: 100 - oxygenLeft,
           dose: mission.radiation.absorbed_mgy_per_day.mean * r.round_trip_walk_h / 24 };
}
function scenarioApplies() {
  return state.target.id === mission.scenario.target && state.routeId === mission.scenario.profile;
}

function drawRealNote() {
  const tg = state.target ?? mission.targets[0], r = tg.routes.find((q) => q.id === 'safest');
  $('spec-real').textContent = t('real_note', { km: (r.distance_m / 1000).toFixed(1), target: tg.name, h: Math.round(r.distance_m / 30) });
}
function drawPanels() {
  drawRealNote();
  if (!state.target) {
    $('f-route').textContent = t('no_target'); $('t-route').textContent = t('no_target');
    return;
  }
  const f = forecast(), r = f.r, safe = mission.grid.safe_slope_deg, reserve = Math.round(mission.crew.oxygen_reserve * 100);
  const name = t('forecast_route', { target: state.target.name, route: t(r.id).toLowerCase() });
  $('f-route').textContent = name;
  $('f-oxygen').textContent = Math.round(f.oxygenLeft);
  $('f-walk').textContent = r.round_trip_walk_h.toFixed(1);
  $('f-battery').textContent = Math.round(f.batteryLeft);
  $('f-dose').textContent = f.dose.toFixed(3);
  $('f-verdict').textContent = t(r.oxygen_ok ? 'verdict_ok' : 'verdict_risk', { r: reserve });
  $('f-verdict').classList.toggle('is-risk', !r.oxygen_ok);

  $('t-route').textContent = name;
  const st = r.stats, rad = mission.radiation, wx = mission.weather;
  const line = (key, k, oxyCell) => `<tr><td>${t(key)}</td><td>${st.slope_deg[k].toFixed(1)}</td>` +
    `<td>${Math.round(st.elevation_m[k])}</td><td>${Math.round(st.thermal_inertia[k])}</td>` +
    `<td>${wx.air_temp_c[k].toFixed(1)}</td><td>${Math.round(wx.pressure_pa[k])}</td><td>${rad.absorbed_mgy_per_day[k].toFixed(3)}</td><td>${oxyCell}</td></tr>`;
  $('t-note').textContent = t('t_note', { a: wx.sols[0], b: wx.sols[1], n: rad.observations, y0: rad.years[0], y1: rad.years[1] });
  const photo = state.target.photo;
  $('t-photo').hidden = !photo;
  if (photo) $('t-photo').src = photo.file;
  $('t-caption').textContent = photo ? t('t_photo', photo) : t('t_caption');
  $('ambient').style.backgroundImage = `url(${photo ? photo.file : 'data/basemap.jpg'})`;
  $('t-body').innerHTML = line('t_min', 'min', '–') + line('t_avg', 'mean', Math.round(f.oxygenUse)) + line('t_max', 'max', '–');

  const reasons = [];
  if (r.above_safe_m > 0) reasons.push(t('r_slope', { over: r.above_safe_m, safe }));
  if (!r.oxygen_ok) reasons.push(t('r_oxygen'));
  if (!r.battery_ok) reasons.push(t('r_battery'));
  if (state.obstacleMet.has(state.target.id + r.id)) reasons.push(t('r_obstacle'));
  $('lamp-risk').classList.toggle('is-on', reasons.length > 0);
  $('lamp-safe').classList.toggle('is-on', reasons.length === 0);
  $('t-reason').textContent = reasons.length ? reasons.join(' · ') : t('r_none');
}

/* ───────────────────────── rover mission ───────────────────────── */
const wait = (ms) => new Promise((ok) => setTimeout(ok, ms));
function log(key, vars, warn) {
  const p = document.createElement('p'); p.textContent = t(key, vars); if (warn) p.className = 'warn';
  $('log').appendChild(p); $('log').hidden = false;
  while ($('log').children.length > 4) $('log').firstChild.remove();
}
function drive(points, seconds, minutes = 0) {
  const cum = [0];
  for (let i = 1; i < points.length; i++) cum.push(cum[i - 1] + points[i].distanceTo(points[i - 1]));
  return new Promise((done) => { state.drive = { points, cum, seconds, minutes, t: 0, done }; });
}
function stepDrive(dt) {
  const d = state.drive; if (!d) return;
  const before = d.t;
  d.t = Math.min(d.t + dt / d.seconds, 1);
  state.clockMin += (d.t - before) * d.minutes;
  $('clock').textContent = t('clock', { h: Math.floor(state.clockMin / 60), m: String(Math.floor(state.clockMin % 60)).padStart(2, '0') });
  const e = d.t < 0.5 ? 2 * d.t * d.t : 1 - 2 * (1 - d.t) * (1 - d.t);
  const s = e * d.cum[d.cum.length - 1];
  let i = 1; while (i < d.cum.length - 1 && d.cum[i] < s) i++;
  const k = (s - d.cum[i - 1]) / Math.max(d.cum[i] - d.cum[i - 1], 1e-6);
  rover.position.lerpVectors(d.points[i - 1], d.points[i], k);
  const ahead = d.points[Math.min(i + 2, d.points.length - 1)];
  if (ahead.distanceToSquared(rover.position) > 1) rover.lookAt(ahead.x, rover.position.y, ahead.z);
  if (state.view === 'path') {  // the camera rides along so the rover stays readable
    controls.target.lerp(rover.position, 0.08);
    landCam.position.lerp(FOLLOW.clone().add(rover.position), 0.035);
  }
  if (d.t >= 1) { state.drive = null; d.done(); }
}
const FOLLOW = new THREE.Vector3(70, 95, 150);

async function sendRover() {
  if (state.busy || !state.target) return;
  state.busy = true; $('send').disabled = true; $('send').textContent = t('rover_busy');
  $('log').innerHTML = ''; extraGroup.clear(); obstacle.visible = false;
  const r = route(), sc = mission.scenario, key = state.target.id + r.id;
  const out = toPoints(r.cells, 1.5, 2);
  rover.visible = true; rover.position.copy(out[0]);
  state.clockMin = 0; $('clock').hidden = false;
  log('log_depart', { route: t(r.id).toLowerCase() });
  await drive(out, 7, r.rover_time_min);
  log('log_arrive', { target: state.target.name, km: (r.distance_m / 1000).toFixed(2), deg: r.max_slope_deg.toFixed(1) });
  await wait(900);
  log('log_return');
  if (scenarioApplies()) {
    const hit = sc.driven_cells.findIndex((c) => c[0] === sc.first_detection_cell[0] && c[1] === sc.first_detection_cell[1]);
    const back = r.rover_time_min * sc.driven_distance_m / sc.planned_distance_m, share = hit / sc.driven_cells.length;
    await drive(toPoints(sc.driven_cells.slice(0, hit + 1), 1.5, 2), 2.6, back * share);
    obstacle.visible = true; state.obstacleMet.add(key);
    log('log_obstacle', {}, true);
    await wait(1100);
    const planned = new Set(sc.planned_cells.map((c) => c[0] + ',' + c[1]));
    let rejoin = hit;
    sc.driven_cells.forEach((c, i) => { if (i > hit && !planned.has(c[0] + ',' + c[1])) rejoin = i; });
    const detour = tube(toPoints(sc.driven_cells.slice(hit, Math.min(rejoin + 8, sc.driven_cells.length)), 5), '#ffffff', 2.2);
    detour.renderOrder = 4; extraGroup.add(detour); reveal(detour, '#ffffff', 0, 1.1);
    log('log_replan', { n: sc.replans, s: sc.repair_total_s.toFixed(2), f: sc.fresh_plan_at_first_detection_s.toFixed(2) });
    await wait(900);
    await drive(toPoints(sc.driven_cells.slice(hit), 1.5, 2), 6, back * (1 - share));
    log('log_home_detour', { d: sc.driven_distance_m - sc.planned_distance_m });
  } else {
    await drive(out.slice().reverse(), 7, r.rover_time_min);
    log('log_home');
  }
  state.busy = false; $('send').disabled = false; $('send').textContent = t('send_rover');
  drawPanels(); await wait(1200); frameRoute();
}

/* ───────────────────────── globe → site ───────────────────────── */
let tween = null;
function flyToSite() {
  const m = onGlobe(JEZERO.lat, JEZERO.lon);
  let ry = Math.atan2(-m.x, m.z);
  while (ry < globe.rotation.y - Math.PI) ry += 2 * Math.PI;
  while (ry > globe.rotation.y + Math.PI) ry -= 2 * Math.PI;
  tween = { t: 0, ry0: globe.rotation.y, ry1: ry, rx1: THREE.MathUtils.degToRad(JEZERO.lat), z0: globeCam.position.z, faded: false };
}
function stepTween(dt) {
  const w = tween; w.t = Math.min(w.t + dt / 2.8, 1);
  const e = w.t * w.t * (3 - 2 * w.t);
  globe.rotation.y = w.ry0 + (w.ry1 - w.ry0) * e;
  globe.rotation.x = w.rx1 * e;
  globeCam.position.z = w.z0 + (1.22 - w.z0) * e * e;
  if (w.t > 0.72 && !w.faded) { w.faded = true; $('fade').classList.add('is-on'); }
  if (w.t >= 1) {
    tween = null;
    setTimeout(() => { setPhase('terrain'); $('fade').classList.remove('is-on'); }, 450);
  }
}
function setPhase(phase) {
  state.phase = phase;
  const site = phase === 'terrain';
  for (const id of ['layers', 'ledger', 'back']) $(id).hidden = !site;
  if (!site) { $('log').hidden = true; globe.rotation.x = 0; globeCam.position.z = 4.4; }
  $('go').textContent = t(site ? 'coords_show' : 'coords_go');
  if (site) refreshTarget(true);
  setPrompt(); fit();
}

/* ───────────────────────── target selection ───────────────────────── */
const metres = (lat1, lon1, lat2, lon2) => {
  const R = 3396190, k = Math.PI / 180;
  return Math.hypot((lat2 - lat1) * k * R, (lon2 - lon1) * k * R * Math.cos(lat1 * k));
};
function refreshTarget(reframe) {
  drawRoutes(reframe); drawLedger(reframe); drawPanels(); setPrompt(); resetEva();
  if (reframe) frameRoute();
}
function setPrompt() {
  const key = state.view === 'astronaut' ? 'prompt_astronaut' : state.view === 'tablet' ? 'prompt_tablet' : state.view === 'rover' ? 'prompt_rover' : state.view === 'sources' ? 'prompt_sources'
    : state.phase === 'terrain' && state.target ? 'prompt_routes' : 'prompt_choose';
  $('prompt').textContent = t(key, { target: state.target?.name });
}
function fillTargets() {
  const sel = $('target-select'), keep = sel.value;
  sel.innerHTML = mission.targets.map((tg) =>
    `<option value="${tg.id}">${tg.name}${tg.kind === 'team' ? ` (${t('team_target')})` : ''}</option>`).join('');
  if (keep) sel.value = keep;
}
function onSubmit(ev) {
  ev.preventDefault();
  const val = (id) => parseFloat($(id).value.replace(',', '.'));
  const [sLat, sLon, eLat, eLon] = ['start-lat', 'start-lon', 'end-lat', 'end-lon'].map(val);
  const g = mission.grid, msg = [];
  if ([sLat, sLon, eLat, eLon].some(Number.isNaN)) { $('coord-msg').textContent = t('msg_bad'); return; }
  if (eLat > g.north_lat || eLat < g.south_lat || eLon < g.west_lon || eLon > g.east_lon) { $('coord-msg').textContent = t('msg_outside'); return; }
  const [bLon, bLat] = mission.base.lonlat;
  if (metres(sLat, sLon, bLat, bLon) > 30) {
    msg.push(t('msg_base')); $('start-lat').value = bLat.toFixed(5); $('start-lon').value = bLon.toFixed(5);
  }
  let best = null, bestD = Infinity;
  for (const tg of mission.targets) {
    const d = metres(eLat, eLon, tg.lonlat[1], tg.lonlat[0]);
    if (d < bestD) { bestD = d; best = tg; }
  }
  if (bestD > 30) msg.push(t('msg_nearest', { name: best.name, d: Math.round(bestD) }));
  $('coord-msg').textContent = msg.join(' ');
  state.target = best; $('target-select').value = best.id;
  if (state.phase === 'globe') flyToSite(); else refreshTarget(true);
}

/* ───────────────────────── suit telemetry and sound ───────────────────────── */
let audio = null, breathTimer = null;
function breathe() {
  const { ctx, gain, filter } = audio, n = ctx.currentTime, g = gain.gain;
  g.cancelScheduledValues(n); g.setValueAtTime(0.0001, n);
  filter.frequency.setValueAtTime(950, n);
  g.linearRampToValueAtTime(0.2, n + 1.2); g.linearRampToValueAtTime(0.0001, n + 1.9);
  filter.frequency.setValueAtTime(520, n + 2.2);
  g.setValueAtTime(0.0001, n + 2.2); g.linearRampToValueAtTime(0.15, n + 2.9); g.linearRampToValueAtTime(0.0001, n + 4.3);
}
function sound(on) {
  if (on && !audio) {
    const ctx = new AudioContext(), buf = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate), d = buf.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    const src = ctx.createBufferSource(); src.buffer = buf; src.loop = true;
    const filter = ctx.createBiquadFilter(); filter.type = 'bandpass'; filter.Q.value = 0.9;
    const gain = ctx.createGain(); gain.gain.value = 0.0001;
    src.connect(filter).connect(gain).connect(ctx.destination); src.start();
    audio = { ctx, gain, filter };
  }
  clearInterval(breathTimer);
  if (!audio) return;
  if (on) { audio.ctx.resume(); breathe(); breathTimer = setInterval(breathe, 4600); } else audio.ctx.suspend();
}
// The walk is replayed on an accelerated clock; suit consumables follow the elapsed walk time.
const eva = { p: 0, playing: false };
const EVA_SECONDS = 18;
let beat = 0;
function resetEva() { eva.p = 0; eva.playing = false; $('eva-play').textContent = t('eva_play'); }
function stepVitals(dt) {
  if (eva.playing) {
    eva.p = Math.min(eva.p + dt / EVA_SECONDS, 1);
    if (eva.p >= 1) { eva.playing = false; $('eva-play').textContent = t('eva_replay'); }
  }
  const hours = state.target ? eva.p * route().round_trip_walk_h : 0;
  const left = Math.max(100 - hours / mission.crew.oxygen_h * 100, 0);
  const heart = eva.playing ? 100 : 76;
  $('v-time').textContent = `${Math.floor(hours)}:${String(Math.floor(hours % 1 * 60)).padStart(2, '0')}`;
  $('v-heart').textContent = heart; $('v-breath').textContent = eva.playing ? 20 : 14;
  $('v-oxygen').textContent = left.toFixed(1); $('v-battery').textContent = left.toFixed(1);
  const c = $('ecg'), x = c.getContext('2d'), w = c.width, h = c.height;
  beat += dt * heart / 60;
  x.clearRect(0, 0, w, h); x.beginPath(); x.strokeStyle = '#c8693b'; x.lineWidth = 2;
  for (let px = 0; px < w; px += 2) {
    const p = ((px / 150 + beat) % 1 + 1) % 1;
    const y = p < 0.06 ? -6 * Math.sin(p / 0.06 * Math.PI) : p < 0.1 ? 0 : p < 0.13 ? -(p - 0.1) / 0.03 * 34
      : p < 0.16 ? -34 + (p - 0.13) / 0.03 * 46 : p < 0.19 ? 12 - (p - 0.16) / 0.03 * 12 : p > 0.3 && p < 0.42 ? -9 * Math.sin((p - 0.3) / 0.12 * Math.PI) : 0;
    px ? x.lineTo(px, h / 2 + 8 + y) : x.moveTo(px, h / 2 + 8 + y);
  }
  x.stroke();
}

/* ───────────────────────── views, language, layout ───────────────────────── */
function fit() {
  const host = $('host-' + state.view), w = host.clientWidth, h = host.clientHeight;
  if (!w || !h) return;
  renderer.setSize(w, h, false);
  // The scene fills the window; shift its centre into the area the panels leave free.
  const wide = window.innerWidth > 900, rail = wide ? 212 : 0;
  const ledger = state.view === 'path' && state.phase === 'terrain' ? $('ledger').offsetHeight + 20 : 0;
  document.documentElement.style.setProperty('--ledger-h', ledger + 'px');
  const dx = !wide ? 0 : state.view === 'rover' ? 100 : state.view === 'path' ? -rail / 2 : 0;
  const dy = wide ? ledger / 2 : state.view === 'path' ? h * 0.24 : 0;  // on phones the scene sits in the top half
  for (const cam of [globeCam, landCam, roverCam, bayCam]) {
    cam.aspect = w / h;
    if (dx || dy) cam.setViewOffset(w, h, dx, dy, w, h); else cam.clearViewOffset();
    cam.updateProjectionMatrix();
  }
}
function setView(view) {
  state.view = view;
  document.querySelectorAll('.tab').forEach((b) => b.classList.toggle('is-active', b.dataset.view === view));
  document.querySelectorAll('.view').forEach((s) => s.classList.toggle('is-active', s.id === 'view-' + view));
  $('host-' + view).appendChild(renderer.domElement);
  const cabin = view === 'tablet';
  land.background = cabin ? SKY : null; land.fog = cabin ? new THREE.Fog(SKY, 120, 2600) : HAZE;
  landStars.visible = !cabin; controls.enabled = view === 'path';
  for (const g of [markGroup, routeGroup, extraGroup]) g.visible = !cabin;
  overlaySlope.visible = !cabin && $('layer-slope').checked;
  overlayThermal.visible = !cabin && $('layer-thermal').checked;
  sound(view === 'astronaut' && state.sound);
  drawPanels(); setPrompt(); fit();
}
function setLang(next) {
  lang = next; document.documentElement.lang = next;
  document.querySelectorAll('[data-lang]').forEach((b) => b.classList.toggle('is-active', b.dataset.lang === next));
  document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
  $('sound').firstElementChild.textContent = t(state.sound ? 'sound_on' : 'sound_off');
  $('eva-play').textContent = t(eva.playing ? 'eva_playing' : eva.p >= 1 ? 'eva_replay' : 'eva_play');
  $('go').textContent = t(state.phase === 'terrain' ? 'coords_show' : 'coords_go');
  fillTargets(); setLegend(); setPrompt(); drawSources();
  if (state.target && state.phase === 'terrain') { drawLedger(); }
  drawPanels();
}
function setLegend() {
  const sw = (c) => `<b style="background:${c}"></b>`;
  $('legend').innerHTML = overlaySlope?.visible
    ? `${sw('#f2b33d')}10–15° ${sw('#ff7828')}15–30° ${sw('#e5484d')}${lang === 'tr' ? '30° üstü' : 'over 30°'}`
    : overlayThermal?.visible ? t('legend_thermal') : '';
}

let last = performance.now();
function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.05); last = now;
  if (state.view === 'path' && state.phase === 'globe') {
    if (tween) stepTween(dt); else globe.rotation.y += dt * 0.05;
    siteMark.material.opacity = 0.55 + 0.45 * Math.sin(now / 350);
    renderer.render(globeScene, globeCam);
  } else if (state.view === 'astronaut') {
    loneStars.rotation.y += dt * 0.01; stepVitals(dt);
    renderer.render(starScene, globeCam);
  } else if (state.view === 'sources') {
    loneStars.rotation.y += dt * 0.006;
    renderer.render(starScene, globeCam);
  } else if (state.view === 'tablet' && state.target) {
    stepDrive(dt);
    const p = world(state.target.cell, 6), a = now / 9000;
    roverCam.position.copy(p); roverCam.lookAt(p.x + Math.cos(a) * 100, p.y - 4, p.z + Math.sin(a) * 100);
    renderer.render(land, roverCam);
  } else if (state.view === 'tablet') {
    renderer.render(starScene, globeCam);
  } else if (state.view === 'rover') {
    turntable.rotation.y += dt * 0.32;
    renderer.render(bay, bayCam);
  } else {
    stepDrive(dt); stepReveals(dt); controls.update();
    renderer.render(land, landCam);
  }
  requestAnimationFrame(frame);
}

async function start() {
  [mission, height] = await Promise.all([
    fetch('data/mission.json').then((r) => r.json()),
    fetch('data/height.bin').then((r) => r.arrayBuffer()).then((b) => new Uint16Array(b)),
  ]);
  const g = mission.grid, span = (g.height_max_m - g.height_min_m) / 65535;
  height = Float32Array.from(height, (v) => g.height_min_m + v * span);
  buildLand();
  const [lon, lat] = mission.base.lonlat;
  $('start-lat').value = lat.toFixed(5); $('start-lon').value = lon.toFixed(5);
  fillTargets(); drawSources();
  const pick = () => {
    const tg = mission.targets.find((x) => x.id === $('target-select').value);
    $('end-lat').value = tg.lonlat[1].toFixed(5); $('end-lon').value = tg.lonlat[0].toFixed(5);
  };
  $('target-select').addEventListener('change', pick); pick();
  $('coords').addEventListener('submit', onSubmit);
  $('send').addEventListener('click', sendRover);
  $('intro-go').addEventListener('click', () => { $('intro').classList.add('is-gone'); document.body.classList.add('started'); });
  $('back').addEventListener('click', () => { if (!state.busy) setPhase('globe'); });
  $('layer-slope').addEventListener('change', (e) => { overlaySlope.visible = e.target.checked; setLegend(); });
  $('layer-thermal').addEventListener('change', (e) => { overlayThermal.visible = e.target.checked; setLegend(); });
  $('eva-play').addEventListener('click', () => {
    if (!state.target) return;
    eva.p = 0; eva.playing = true; $('eva-play').textContent = t('eva_playing');
  });
  $('sound').addEventListener('click', () => {
    state.sound = !state.sound; $('sound').setAttribute('aria-pressed', state.sound);
    $('sound').firstElementChild.textContent = t(state.sound ? 'sound_on' : 'sound_off'); sound(state.sound);
  });
  document.querySelectorAll('.tab').forEach((b) => b.addEventListener('click', () => setView(b.dataset.view)));
  document.querySelectorAll('[data-lang]').forEach((b) => b.addEventListener('click', () => setLang(b.dataset.lang)));
  new ResizeObserver(fit).observe(document.body);
  window.addEventListener('resize', () => { fit(); if (state.target && state.phase === 'terrain') drawLedger(); });
  setLang(lang);
  setView('path');
  requestAnimationFrame(frame);
}
start();
