# Evidence table: do subsidies and public spending drive growth and local activity?

Belgium focus. Compiled 2026-11-14. Every number below was read in a source, unless marked "(not verified)".
"GAP" means we looked and did not find it. Studies are cited by author and year, with links.
This file supports the myth card in [article.md](article.md). It was reviewed before publication.

## Scale of Belgian business support
The NBB (Revue economique, Oct 2025) puts Belgian business subsidies and investment aid at about EUR 25bn in 2024, just over 4% of GDP, about 1.5pp of GDP above neighbours. About two-thirds are wage subsidies (withholding-tax exemptions, targeted social-contribution cuts, service-voucher subsidies) that offset high labour taxation. The ~3% ESA D3 figure is narrower; the 4% figure includes investment aid. Source: https://blog.forumforthefuture.be/fr/article/les-subventions-aux-entreprises-sont-elles-elevees-en-belgique-/28952 and https://www.vrt.be/vrtnws/nl/2025/10/27/overheidssubsidies-aan-bedrijven-bedroegen-in-2024-25-miljard-eu/

## Evidence table
How to read the table. Method key: RDD = regression discontinuity; DiD = difference-in-differences; PSM = matching; IV; MACRO = simulation model (not causal identification); CORR = correlational; DESC = descriptive audit.

| # | Instrument | Belgian cost/yr | Study (author, year, method) | Effect found | Verdict | Confidence | URL |
|---|---|---|---|---|---|---|---|
| 1 | Partial exemption from withholding tax, R&D staff | EUR 1.6bn in 2024 (spending review, Aug 2026; R&D regime only) | Dumont (FPB, 2013 first eval; 2019; 4th eval 2022), firm-level econometrics on R&D Policy Mix databank 2003-2019, several estimators for selection | Robust additionality: firms spend more own R&D beyond the aid received. Numeric "bang for the buck" only in a graph not read: GAP | Works (for R&D inputs); no evidence on growth or productivity | Medium-high | https://ideas.repec.org/p/pra/mprapa/115418.html ; https://ideas.repec.org/p/fpb/wpaper/201301.html |
| 1b | Same, Aug 2026 federal spending review | Combined withholding-tax exemptions EUR 4.4bn (2024): R&D 1.6bn, night/shift 2.0bn, overtime 0.2bn, other ~0.53bn | Federal spending review, 31 Aug 2026 (via Deloitte summary), DESC | Objectives unclear; users more labour-intensive but this reflects a labour-intensive mix, not shown to be job creation | Unproven for shift/night/overtime | Medium (secondary summary; original not read) | https://www.deloitte.com/be/en/services/tax/blogs/spending-review-on-withholding-tax-exemptions.html |
| 2a | R&D tax deduction (investment deduction) | Total corporate R&D tax incentives EUR 2.8bn (2019) | Dumont (FPB 2022), econometrics | Only CIT incentive with evidence of additionality | Mixed | Medium | https://blog.forumforthefuture.be/fr/article/recherche-et-developpement-en-belgique-une-nouvelle-evaluation-de-laide-publique/17138 |
| 2b | R&D tax credit; patent income deduction (abolished 2021) | Included in EUR 2.8bn | Dumont (FPB 2022) | Thin evidence of additionality | No evidence / weak | Medium | same |
| 2c | Innovation income deduction (since 2016) | Included in EUR 2.8bn | Dumont (FPB 2022) | Robust evidence of crowding-out (funds R&D that would occur anyway) | Harmful to cost-effectiveness (windfall) | Medium | same |
| 3 | Flemish R&D grants (IWT/VLAIO) | Sample: 3,019 projects, ~EUR 628m over 2004-2010 (~EUR 90m/yr) | Lopes-Bento and Czarnitzki et al., treatment-effect models, Research Policy/ZEW | Additional R&D spending and employment; not reduced by other subsidies, repeat funding or multiple projects. Reported ~16,800 person-years R&D jobs (implied ~EUR 37k per person-year, our arithmetic). Per-euro input additionality: GAP | Works (R&D inputs) | Medium | https://www.zew.de/PU69212-1 |
| 4a | Walloon competitiveness clusters | Plan Marshall 4.0: EUR 631m earmarked; 378 projects, ~EUR 1.14bn public+private (calls 1-24); earlier eval: ~EUR 450m, 72% public | Dujardin, Louis, Mayneris (IWEPS RR25, 2019), DiD + triple-diff + PSM, 191 funded firms vs ~15,500 controls | Small, short-lived employment and value-added gains, not significant under nearest-neighbour matching; no productivity or TFP effect; no export-value effect. Policy selected already strong firms. IWEPS's report conclusion: faster growth in jobs, VA, exports; R&D effect "mixed". | Mixed (modest) | Medium-high (causal design, but small effects) | https://perso.uclouvain.be/florian.mayneris/papers/DLM_reru.pdf ; https://www.iweps.be/wp-content/uploads/2019/05/RR25-PM4-Louis-complet.pdf |
| 4b | Walloon clusters, 2014 thematic evaluation | see above | IWEPS thematic evaluation 2014, surveys, case studies, DESC | 5,423 jobs "created or maintained" per pole directors; 78% of projects with data delivered under half the promised jobs; attribution not possible | No evidence (self-reported) | Low | https://www.iweps.be/wp-content/uploads/2017/02/evaluation_thematique_poles.pdf |
| 4c | Walloon Recovery Plan (PRW) 2021+ | Firm investment subsidies ~EUR 1.07bn (14.8% of PRW), R&D aid ~EUR 540m | Verschueren (IWEPS RR56, 2023), MACRO hybrid growth model | Simulated GDP about +0.7% by 2030, +0.6% by 2040 vs no plan; assumes productive-capital channel, not measured | Unproven (model assumption) | Low | https://www.iweps.be/wp-content/uploads/2023/10/RR56.pdf |
| 4d | Walloon research aid (audit) | GAP | Cour des comptes audit | Objectives never made measurable; steering on means not performance; no impact measurement | No evidence (cannot be evaluated) | Medium | https://blog.forumforthefuture.be/fr/article/les-aides-a-la-recherche-en-region-wallonne-sous-la-loupe-de-la-cour-des-comptes/23841 |
| 5a | EU Objective 1, EU-wide | Not Belgium-specific | Becker, Egger, von Ehrlich (2010, J. Public Econ.), RDD at 75% GDP/capita, 1,213 NUTS3, 1989-2006 | About +1.8pp per year GDP/capita growth in treated regions (IV ~2.6%); no robust employment effect; about EUR 1.21 extra GDP per EUR transferred (author calls this conservative); effect fades above ~1.25% of regional GDP in transfers | Works (income growth), not jobs | High | https://www.ifo.de/DocDL/cesifo1_wp2495.pdf |
| 5b | EU regional policy, persistence | Not Belgium-specific | Becker, Egger, von Ehrlich (2018, Reg. Sci. Urban Econ.), RDD, 1989-2013 | Gains positive but not long-lived; losing status reverses them; weaker during the crisis | Mixed (temporary) | High | https://econpapers.repec.org/RePEc:eee:regeco:v:69:y:2018:i:c:p:143-152 |
| 5c | Objective 1 Hainaut 1994-2006 | GAP | Vandenberghe (2018, Economics E-Journal), DiD with growth-rate parallel-paths assumption, municipal taxable income/head | Level-DiD shows income gap widening (-EUR 426 in 2000, -507 in 2007); growth-rate DiD shows +EUR 492 (2000) rising to +EUR 1,329 (2007) vs rest of Belgium. Conclusion hinges on identifying assumption. Employment not analysed | Mixed / contested | Low-medium | https://research.dial.uclouvain.be/bitstreams/541d3799-4dd8-4758-97c6-43862247e1f6/download |
| 5d | EU Cohesion Policy 2007-13 (Commission ex-post) | Not Belgium-specific; EUR 346.5bn invested EU-wide | European Commission ex-post evaluation (2016), MACRO | EUR 2.74 extra GDP per EUR invested by 2023; ~1m jobs | Unproven as causal (model-based; vs 1.21 from RDD) | Low-medium | https://ec.europa.eu/regional_policy/sources/evaluation/expost2013/wp1_synthesis_factsheet_en.pdf |
| 6a | First-hire payroll-tax cut | GAP (part of ~two-thirds wage-subsidy share of EUR 25bn) | NBB (Oct 2025) review of wage subsidies, as summarised by OECCBB; Toniolo (UCLouvain 2025), structural model | NBB: over EUR 100,000 per additional job on average. Toniolo: reduction did not address expansion constraints; minimal hiring change among firms that would have hired anyway | Mostly no effect (high cost per job) | Medium (secondary source for the EUR 100k) | https://blog.oeccbb.be/nl/article/subsidies-minder-uitgeven-of-beter-besteden/29006 ; https://research.dial.uclouvain.be/entities/publication/06c0d1a4-2432-465c-98e6-7df5ee3f96f1 |
| 6b | Reduced contributions for older workers | GAP | NBB, as summarised by OECCBB | Hardly lengthened careers | No evidence of effect | Medium (secondary) | same OECCBB link |
| 6c | Win-Win youth hiring subsidy 2010-11 | GAP | Albanese, Cockx, Dejemeppe (IRES 2022/19), donut RDD at age 26 + DiD | +10pp transition to private jobs within 1 yr; no overall employment gain for graduates (public/self-employment fell); gains vanished for dropouts; fully deadweight near Luxembourg border; net public cost near zero long run but CI includes zero | Mixed | High | https://sites.uclouvain.be/econ/DP/IRES/2022019.pdf |
| 6d | Work bonus (employee contribution cut) | Cost not reported | Ex-post FPB-type evaluation (via Forum for the Future), matching + DiD | Higher chance of staying employed; hours effect small and rarely significant; negative effect on wage growth, worst for over-50s | Mixed | Medium | https://blog.forumforthefuture.be/nl/article/evaluatie-van-de-maatregel-werkbonus-welke-impact-op-de-lonen-en-de-werkgelegenheid-/23647 |
| 6e | Night/shift/overtime withholding exemptions | EUR 2.0bn + 0.2bn (2024) | Federal spending review, Aug 2026 | No job-creation evidence found | Unproven | Medium | see 1b |
| 6f | Macro model of 1995-2000 contribution cuts | GAP | FPB WP 2003-14, macro labour model | Employment gains not stated in abstract: GAP | Not assessed | n/a | https://ideas.repec.org/p/fpb/wpaper/200314.html |
| 7 | Service vouchers | Flanders only: gross EUR 1.30bn (2016), of which subsidies EUR 1.11bn; net EUR 260m after return effects (2017). Federal total: GAP | Flemish Dept of Work evaluations (2016 gross cost; 2017 return effects; consultant not confirmed as IDEA), accounting return-effect calculation; IZA DP 8717 (2014; authors not verified), descriptive and partial evidence | Return effects ~85% of gross cost; net cost EUR 5,650 per FTE (2017); 84,397 workers in Flanders. Also: many workers stay in voucher jobs; some displacement of regular workers; users are mostly higher-income households | Works on formalisation and jobs; mixed on stepping stone and equity | Medium (accounting, not causal) | https://www.vvsg.be/Leden/Werk%20%26%20Activering/WERK/Managementsamenvatting%20-%20Terugverdieneffecten%20dienstenchequestelsel%20VL.pdf ; https://ideas.repec.org/p/iza/izadps/dp8717.html |
| 8 | Company cars / fuel cards | EUR 3-6bn lost revenue per year (range, FPB, June 2025 press summary) | Federal Planning Bureau (2025), fiscal simulation | Replacing the regime would yield ~EUR 5.2bn/yr more by 2028; ~70% of cars go to top two income groups; helped fleet electrification | Harmful on revenue and equity; no growth evidence | Medium (press summary) | https://newmobility.news/en/2025/06/27/planning-bureau-belgiums-company-car-tax-perks-cost-e6-billion/ |
| 9 | Flemish green certificates, solar 2006-12 | Estimated total solar support EUR 12.2bn through 2032 (2016 estimate); onshore wind 1.3bn | EnergyVille fact check (2016), cost estimate only | Capacity 2.2 GWe, 91% installed 2009-12 (over-subsidised, support later made adjustable). Local jobs/growth causal evaluation: GAP | Works for capacity; unproven for growth; costly | Low-medium | https://energyville.be/en/news/fact-check-how-much-support-has-already-been-pledged-wind-and-solar-energy-flandersbelgium |
| 10 | Regional investment aid (Wallonia, Flanders, Brussels) | Walloon PRW firm investment subsidies ~EUR 1.07bn (plan total); others GAP | IWEPS thematic evaluation on free zones exists (URL only, not read); no causal Belgian study found | 2014 cluster evaluation notes investment aid was little used and likely windfall | No evidence | Low | https://www.iweps.be/wp-content/uploads/2017/02/evaluation_thematique_zones_franches.pdf |

## International benchmarks
| Benchmark | Study | Finding | Verdict |
|---|---|---|---|
| Netherlands WBSO | Dialogic/SEO evaluation 2018-22 | Preferred estimate EUR 0.41 extra R&D per EUR of tax reduction; incentive weakens over time; implementation cost 1.4% of budget | Mixed (below 1:1) |
| UK R&D tax relief | Dechezleprêtre et al. (NBER 22405), RD at size threshold, 2006-11 | Elasticity ~2.6; GBP 1.7 private R&D per GBP 1 tax cost; SME 2.1-2.8, large firms ~1.4; business R&D ~10% lower without it. Sample is small credit-constrained firms near the threshold | Works for inputs; says nothing on growth |
| Place-based policy | Neumark and Simpson (Handbook, 2015); FRBSF letter | Eight enterprise-zone studies: first five find no employment effect, last three find large positive; federal Empowerment Zones with big grants did better; housing prices rise (owners capture benefits); possible displacement from neighbours | Mixed |
| Local fiscal multipliers | Chodorow-Reich (NBER 23577) | Preferred cross-sectional multiplier 1.8; a rough lower bound for a closed-economy zero-lower-bound national multiplier. Nakamura-Steinsson (~1.5): primary source not fetched, not verified. These measure transfers across US regions in a monetary union and are not subsidies to firms | Works short run for demand, not for supply-side subsidies |
| Government size and growth | Bergh and Henrekson (2011), survey | In rich countries, +10pp government size goes with 0.5 to 1pp lower annual growth; authors warn against a causal reading; transfers look worse than investment; Nordic exceptions explained by trust/compensating policies | Correlational, negative |

## Synthesis (10 lines)
1. Most credible Belgian evidence concerns R&D inputs: the researcher withholding-tax exemption and regional grants raise firms' own R&D beyond the aid received (FPB, Czarnitzki et al.).
2. The same evidence is silent on growth, productivity or jobs outside R&D; input additionality is not output.
3. Corporate-tax R&D incentives are weaker: deduction mixed, credit and patent box thin, innovation income deduction shows crowding-out (FPB 2022).
4. Cluster policy (Wallonia) shows small, short-lived job and value-added gains, no productivity or export-value effect; the stronger claims rest on self-reports or models.
5. Wage subsidies, two-thirds of the EUR 25bn, are the least evidenced: first-hire cuts cost over EUR 100k per extra job (NBB) and older-worker cuts barely moved careers.
6. Service vouchers are the best documented large item: return effects ~85% in Flanders, net ~EUR 5.7k per FTE, but weak stepping-stone and regressive use.
7. Place-based EU funds raise regional income growth (RDD, about 1.8pp a year; ~EUR 1.2 per EUR) but not employment, with diminishing returns past ~1.25% of regional GDP.
8. Persistence is poor: effects fade and reverse after funds end (Becker et al. 2018); Hainaut evidence depends on the DiD assumption.
9. The Commission's EUR 2.74 per EUR is a model output, about double the quasi-experimental estimate.
10. Large Belgian instruments with no causal evaluation found: shift/night exemptions, company cars (revenue loss, not growth), regional investment aid, green certificates.

## Our own test: Hainaut and EU Objective 1 (1994-2006)

Code: `run.py`. Outputs: `outputs/hainaut_objective1_test.csv`, `outputs/hainaut_growth_gaps.csv`,
`outputs/relative_gdp_per_head_index.csv`. Data: JRC ARDECO, NUTS2, version 2024.

What it shows:
- Hainaut's real GDP per head was 74.5% of the Belgian level in 1980, 69.4% in 1993, 64.8% in 2006 and 61.2% in 2024.
- The index fell about 0.4 points a year before 1994 and about 0.35 a year during Objective 1.
- Against Belgium and Flanders there was no pause in the relative decline during the programme. Against the
  rest of Wallonia and Liege the gap in growth narrowed, because those regions also slid during 1993-2006.
- Jobs per head rose 1.8 points in Hainaut over 1993-2006, against 2.8 in the rest of Wallonia, 3.6 in Liege and 3.1 in Belgium.

What it cannot show:
- There is one treated region and no standard errors.
- The result depends on the comparison region and on where the "before" window starts. Moving the start from 1980 to 1985 flips the sign of the change against the rest of Wallonia. See `hainaut_growth_gaps.csv`.
- The comparison regions were also treated. Liege had Objective 2 status, Namur and Luxembourg had Objective 5b status, and Nord-Pas-de-Calais had Objective 1 areas in 1994-99. EU support to Hainaut continued after 2006.
- Pre-1995 values are back-casts. GDP is measured where people work, population where they live.
- Vandenberghe (2018, row 5c) finds that the answer flips with the identifying assumption.

So the test can rule out a large effect, in line with the average effect found by Becker, Egger and von Ehrlich (about
1.8 points of extra growth a year). It cannot say whether Hainaut would have fallen faster without the money.
A synthetic control on disposable income by place of residence would be a better design. It is not done yet.

A cross-country comparison of subsidies and growth was tried and dropped. It was driven by one country, Ireland,
whose GDP is distorted by multinationals, and the definition of subsidies differs across countries.

## Known gaps

- The numeric "bang for the buck" of the researcher withholding-tax exemption (Dumont, graph in a Planning Bureau report).
- The federal total cost and a net evaluation of service vouchers.
- Jobs per euro million, from the High Council for Employment.
- The original federal spending review of August 2026 (read only through a summary).
- Brussels and Flemish investment-aid evaluations.
- A primary source for Nakamura and Steinsson.
- A causal evaluation of solar and green-certificate support on local jobs and growth.
