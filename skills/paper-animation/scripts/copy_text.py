"""All copy is fictional. {K} marks the highlighted keyword."""

FILLER = [
    "The city council approved a measure to extend opening hours at all public recreation centers through the summer months.",
    "Residents of the northern district gathered on Thursday evening to discuss proposed changes to the bus network.",
    "The report estimates the total cost of necessary repairs at approximately one hundred and fifty million dollars over the next five years.",
    "A delegation of foreign ministers toured the city's innovation district on Monday, meeting with local officials to discuss partnerships.",
    "Park rangers reported a significant increase in visitors during the holiday weekend, prompting calls for additional staff.",
    "The annual arts festival drew record crowds this year, with organizers estimating that more than forty thousand visitors passed through the grounds.",
    "Local authorities confirmed that the restoration project at the old library would proceed as planned despite recent delays.",
    "The school board voted unanimously to approve a new curriculum for the upcoming academic year.",
    "A newly published audit of the county's water treatment facilities revealed that several aging plants require significant upgrades.",
    "Officials are advising hikers to avoid the northern trails while crews clear debris left by last week's storm.",
    "The regional council of governors approved a shared services agreement that will allow smaller municipalities to pool resources.",
    "Farmers in the valley say this season's harvest is the strongest in more than a decade, crediting a mild spring.",
    "The ombudsman released a statement broadening the scope of the inquiry following complaints from the public.",
    "Construction crews broke ground on a new performing arts center in the civic plaza on Wednesday morning.",
    "The mayor's office released a comprehensive plan to address homelessness, proposing the construction of transitional housing facilities.",
    "Investigators released new details about the incident and said they will present their findings next month.",
    "A panel of economists warned that rising housing costs continue to outpace wage growth in many metropolitan areas.",
    "The metropolitan water district completed construction of a new desalination plant capable of producing twenty million gallons a day.",
    "Shoppers lined up before dawn as the market reopened following a three-month renovation of its historic hall.",
    "Police are investigating a series of break-ins that occurred in the warehouse district over the past two weeks.",
    "The symphony announced its new season lineup, featuring both classic repertoire and works by emerging composers.",
    "A severe thunderstorm knocked out power to more than twenty thousand homes across the eastern part of the county.",
    "The state transportation department said the bridge will remain closed to vehicle traffic until the inspection is complete.",
    "Small business owners raised concerns about parking restrictions along the waterfront during peak tourist season.",
    "The university announced a partnership with local hospitals to expand training programs for nurses and technicians.",
    "Volunteers planted more than two thousand trees along the riverbank as part of a citywide greening effort.",
    "The board of education released its annual report card for the district, showing modest gains in reading proficiency.",
    "A newly formed committee will review the city's emergency response procedures and report back by the end of the year.",
    "Analysts expect the central bank to hold interest rates steady when it meets later this month.",
    "The museum's new wing, funded largely by private donations, will open to the public in the spring.",
    "Engineers completed an extensive study of safety at intersections near schools and recommended new crossing signals.",
    "The county fair opened on Monday with a record number of exhibitors showcasing livestock, produce, and handmade goods.",
    "Startups in the region raised more money in the first half of the year than in all of last year combined.",
    "Retailers reported strong sales over the weekend, though many warned that supply chain pressures remain.",
    "The technology committee recommended upgrading the municipal network infrastructure, including public wireless access.",
    "Researchers at the state university published a study suggesting that commute times have fallen since the new rail line opened.",
    "Neighborhood leaders organized a petition opposing the proposed relocation of the bus depot to a site near the elementary school.",
    "The fire department responded to a three-alarm blaze at the corner of Maple and Fifth Street early Tuesday morning.",
    "Lawmakers adjourned without reaching an agreement on the budget, setting up a tense final week of negotiations.",
    "The chamber of commerce held its annual luncheon, honoring several longtime business owners for their contributions.",
    "Developers unveiled plans for a mixed-use tower that would include apartments, offices, and a rooftop public garden.",
    "Several companies announced plans to expand their offices downtown, citing the area's growing pool of skilled workers.",
    "Teachers said the new tablets had changed the way students approach homework, for better and for worse.",
    "The consumer protection agency issued a warning about a wave of fraudulent messages targeting older residents.",
    "Health officials urged residents to get vaccinated ahead of the flu season, which is expected to arrive early this year.",
    "A local bakery celebrated its fiftieth anniversary with free pastries and a street party that lasted well into the night.",
    "Commuters faced lengthy delays on Friday after a signal failure halted service on two of the city's busiest lines.",
    "The commission is expected to vote on the proposal at its next meeting, scheduled for the second week of the month.",
    "Economists noted that consumer spending has remained resilient despite higher prices for groceries and fuel.",
    "The library will extend its digital lending catalog to include more than fifty thousand titles, audiobooks, and magazines.",
]

FILLER_HEADS = [
    "Public Wi-Fi Expansion Proposed", "Symphony Announces Season Lineup", "Historic Theater Faces Demolition Vote",
    "Prescription Rules Tightened", "Revenues Exceed Projections", "Emergency Room Expansion Complete",
    "School Board Unveils Revised Curriculum", "Counterfeit Product Warning Issued", "Architect Receives National Design Award",
    "Regional Economy Shows Mixed Signals", "Bus Depot Relocation Faces Opposition", "Restoration Project Moves Forward",
    "Arts Grants Awarded to Local Groups", "Port Authority Approves Dredging", "Pension Fund Reports Strong Returns",
    "Rail Line Ridership Climbs", "Council Delays Vote on Parking Fees", "Farmers Market Returns to Square",
    "Storm Cleanup Continues Across County", "New Bridge Opens to Cyclists", "Startup Funding Hits Record High",
    "Housing Costs Outpace Wages", "Hospital Breaks Ground on New Wing", "City Tightens Budget Ahead of Winter",
]

# Keyword copy is phrase-agnostic: {K} is always used as a noun phrase and no
# verb agrees with it, so any word or phrase reads naturally.
KW_SENT = [
    "Officials said the debate over {K} would be reviewed by an independent panel before the end of the year.",
    "The chief of staff addressed questions about {K}, promising a full report to the council next month.",
    "Critics argue that the rush toward {K} has outpaced the rules meant to govern it.",
    "Teachers say conversations about {K} have become a regular part of the school day.",
    "Business leaders described {K} as one of the most important shifts of the decade.",
    "The committee will spend the next six months examining the impact of {K} on local jobs.",
    "Investors poured record sums into {K} during the first quarter of the year.",
    "Lawmakers are drafting new guidelines for {K} after a wave of complaints from residents.",
    "The mayor said the city would invest in {K} to cut wait times at its busiest service centers.",
    "Few topics have moved as quickly as {K} from the margins into everyday life.",
    "Parents and teachers remain divided over how much attention {K} deserves.",
    "A survey released on Tuesday found that interest in {K} has tripled since spring.",
    "Retailers say demand for {K} has quickly outpaced their most optimistic forecasts.",
    "Consumer advocates urged residents to read the fine print before signing up for {K}.",
    "Small businesses are turning to {K} to stay competitive as costs continue to rise.",
    "Analysts expect spending on {K} to double again before the end of next year.",
]

KW_HEADS = [
    "Debate Over {K} Heats Up", "City Council Weighs {K} Rules", "The Quiet Rise of {K}",
    "Why Everyone Is Talking About {K}", "Regulators Turn to {K}", "Small Businesses Bet Big on {K}",
    "Can We Trust {K}?", "Officials Review {K} Policy", "Watchdog Monitors {K}",
    "Inside the Race for {K}", "The {K} Boom Has Arrived", "Parents Divided Over {K}",
    "Investors Pile Into {K}", "Schools Rethink {K}",
]

KW_QUOTES = [
    "\u201cEvery industry is now asking the same question about {K}.\u201d",
    "\u201cWe are only at the beginning of what {K} can do.\u201d",
    "\u201cThe conversation about {K} has moved to kitchen tables.\u201d",
    "\u201cNobody saw {K} coming this fast.\u201d",
]

KW_TABLOID = ["THE {K} BOOM!", "{K} MANIA", "{K} FRENZY!", "THE {K} CRAZE"]

KICKERS = ["TECHNOLOGY", "BUSINESS", "THE FUTURE", "INNOVATION", "CULTURE", "SPECIAL REPORT"]
SITES = ["The Byline", "NEWSDESK", "Signal Daily", "The Current", "Dispatch", "Morning Wire"]
MASTHEADS = ["The Morning Ledger", "The Evening Courier", "The Daily Record", "Metro Herald"]
NAMES = ["Maya Ortiz", "Daniel Reyes", "Priya Nair", "Tom Ellison", "Sara Kim", "Omar Haddad", "Lena Fischer"]
TEASERS = [
    "How the new rail line changed commutes", "Inside the city's plan for affordable homes",
    "Five takeaways from the budget fight", "The bakery that refused to close", "What rising rates mean for renters",
    "Why startups are moving downtown", "The quiet comeback of the public library", "Storm season: how to prepare",
    "Meet the volunteers replanting the riverbank", "Is the four-day week here to stay?", "The hidden cost of free shipping",
]
