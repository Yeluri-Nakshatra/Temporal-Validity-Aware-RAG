"""
TempRev benchmark builder.

Each reversal item records a real-world fact that changed, with a stale document
(written as if published before the change) and a current document (published at or
after the change). Documents are rendered with varied date-header formats so that the
temporal metadata extractor has to do real work. A subset of items is flagged
`undated_old`, which strips every date cue from the stale document to exercise the
abstention path.

Run:  python build_benchmark.py  -> writes temprev.json next to this file.
"""
import json, hashlib, pathlib

R = []  # reversal items
C = []  # control (non-temporal) items


def rev(id, domain, question, old_answer, old_aliases, new_answer, new_aliases,
        old_title, old_date, old_body, new_title, new_date, new_body,
        change_date=None, new_effective=None, undated_old=False, t_past=None):
    R.append(dict(
        id=id, domain=domain, question=question,
        old=dict(answer=old_answer, aliases=old_aliases, title=old_title, date=old_date, body=old_body),
        new=dict(answer=new_answer, aliases=new_aliases, title=new_title, date=new_date, body=new_body,
                 effective=new_effective),
        change_date=change_date or new_effective or new_date,
        undated_old=undated_old, t_past=t_past,
    ))


def ctl(id, domain, question, answer, aliases, title, date, body):
    C.append(dict(id=id, domain=domain, question=question, answer=answer, aliases=aliases,
                  title=title, date=date, body=body))

# --------------------------------------------------------------------------------------
# SCIENCE
# --------------------------------------------------------------------------------------
rev("sci-pluto", "science",
    "How is Pluto classified by the International Astronomical Union?",
    "a planet (the ninth planet of the Solar System)", ["ninth planet", "a planet", "planet of the solar system"],
    "a dwarf planet", ["dwarf planet"],
    "Introduction to the Solar System: the nine planets", "1999-03-10",
    "The Solar System contains nine planets orbiting the Sun. In order from the Sun they are Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune and Pluto. Pluto, discovered in 1930 by Clyde Tombaugh, is the smallest and most distant planet and is classified as a planet by the International Astronomical Union.",
    "IAU General Assembly resolution on the definition of a planet", "2006-08-24",
    "The International Astronomical Union has adopted a formal definition of the term planet. Under the new definition a planet must orbit the Sun, be nearly round, and have cleared the neighbourhood around its orbit. Pluto does not meet the third criterion and is therefore reclassified as a dwarf planet. The Solar System now has eight planets.")

rev("sci-kilogram", "science",
    "How is the kilogram defined in the International System of Units (SI)?",
    "as the mass of the International Prototype Kilogram, a platinum-iridium cylinder kept near Paris",
    ["international prototype", "platinum", "prototype kilogram", "physical artefact", "physical artifact", "cylinder"],
    "by fixing the numerical value of the Planck constant", ["planck"],
    "SI base units explained: the kilogram", "2012-06-05",
    "The kilogram is the only SI base unit still defined by a physical artefact. It is equal to the mass of the International Prototype Kilogram, a cylinder of platinum-iridium alloy kept at the International Bureau of Weights and Measures near Paris. National copies are periodically compared against the prototype.",
    "Redefinition of the SI base units comes into force", "2019-05-20",
    "The revised International System of Units is now in force. The kilogram is defined by taking the fixed numerical value of the Planck constant h to be 6.62607015 x 10^-34 joule seconds. The International Prototype Kilogram no longer has any role in the definition of the unit. This notice supersedes earlier descriptions of the kilogram as an artefact-based unit.",
    new_effective="2019-05-20")

rev("sci-elements", "science",
    "How many chemical elements are officially named and recognised by IUPAC in the periodic table?",
    "114", ["114", "one hundred and fourteen"],
    "118", ["118", "one hundred and eighteen"],
    "Status of the periodic table: named elements", "2013-02-18",
    "The periodic table currently contains 114 officially named elements, the most recent additions being flerovium (element 114) and livermorium (element 116). Claims for elements 113, 115, 117 and 118 remain under review and these elements have not yet been formally recognised or named.",
    "IUPAC announces the names of four new elements", "2016-11-28",
    "IUPAC has approved the names nihonium (113), moscovium (115), tennessine (117) and oganesson (118). With these additions the seventh row of the periodic table is complete and the table now contains 118 officially named elements. This announcement supersedes the earlier provisional status of these elements.")

rev("sci-tallest", "science",
    "What is the tallest building in the world?",
    "Taipei 101", ["taipei"],
    "the Burj Khalifa in Dubai", ["burj khalifa", "burj"],
    "World's tallest buildings: a record list", "2007-04-02",
    "At 508 metres including its spire, Taipei 101 in Taiwan holds the title of the world's tallest building, a record it has held since its completion. It surpassed the Petronas Towers in Kuala Lumpur, which previously held the record.",
    "Burj Khalifa officially opened as the world's tallest building", "2010-01-04",
    "The Burj Khalifa in Dubai has been officially inaugurated and, at 828 metres, is now the tallest building in the world by a wide margin. It replaces Taipei 101 as the record holder.")

rev("sci-saturn-moons", "science",
    "How many confirmed moons does Saturn have?",
    "146", ["146", "one hundred and forty-six"],
    "274", ["274", "two hundred and seventy-four"],
    "Saturn overtakes Jupiter with 146 confirmed moons", "2023-05-12",
    "Following the recognition of 62 newly confirmed satellites by the Minor Planet Center, Saturn now has 146 confirmed moons, the most of any planet in the Solar System, ahead of Jupiter.",
    "128 new moons of Saturn confirmed, bringing the total to 274", "2025-03-11",
    "The International Astronomical Union's Minor Planet Center has ratified 128 additional moons of Saturn discovered using the Canada-France-Hawaii Telescope. Saturn's confirmed moon count rises to 274. This supersedes the previously reported total.")

# --------------------------------------------------------------------------------------
# SOFTWARE / TECHNOLOGY
# --------------------------------------------------------------------------------------
rev("sw-python2", "software",
    "Is Python 2 still officially supported by the Python core developers?",
    "yes, Python 2.7 continues to receive maintenance and security updates", ["yes", "supported", "continues to receive", "maintained"],
    "no, Python 2 has reached end of life and is no longer supported", ["end of life", "end-of-life", "no longer supported", "not supported", "unsupported", "eol"],
    "Python 2.7 maintenance status", "2015-04-14",
    "Python 2.7 remains an officially supported release series. The core developers continue to publish bug-fix and security releases of Python 2.7, and users may continue to rely on it in production. Python 3 is recommended for new projects.",
    "Sunsetting Python 2: end of life reached", "2020-01-01",
    "Python 2 has reached its end of life. The core developers no longer provide any updates, bug fixes or security patches for Python 2.7. All users should migrate to Python 3. This notice supersedes earlier statements about continued Python 2.7 maintenance.",
    undated_old=True)

rev("sw-github-branch", "software",
    "What is the default branch name for new repositories created on GitHub?",
    "master", ["master"],
    "main", ["main"],
    "Creating a repository on GitHub", "2019-02-11",
    "When you create a new repository on GitHub, an initial branch named master is created automatically. Commits are added to master unless you create and switch to another branch.",
    "GitHub changes the default branch name for new repositories to main", "2020-10-01",
    "All new repositories created on GitHub now use main as the name of the default branch instead of master. Existing repositories are not affected unless their owners rename the branch. This supersedes the earlier default.")

rev("sw-twitter-x", "software",
    "What is the current brand name of the social media platform originally launched as Twitter?",
    "Twitter", ["twitter"],
    "X", ["x"],
    "About Twitter", "2021-06-30",
    "Twitter is a microblogging and social networking service on which users post and interact with short messages known as tweets. The service is operated by Twitter, Inc. and uses a blue bird as its logo.",
    "Twitter rebrands as X", "2023-07-24",
    "The platform formerly known as Twitter has been rebranded as X. The blue bird logo has been retired and replaced by a stylised letter X, and the service is now operated by X Corp. This supersedes all earlier branding.")

rev("sw-meta", "software",
    "What is the name of the parent company of Facebook, Instagram and WhatsApp?",
    "Facebook, Inc.", ["facebook, inc", "facebook inc", "facebook"],
    "Meta Platforms, Inc.", ["meta"],
    "Facebook, Inc. corporate overview", "2020-09-15",
    "Facebook, Inc. is the parent company that owns and operates the Facebook social network as well as Instagram, WhatsApp and Messenger. The company is headquartered in Menlo Park, California.",
    "Facebook company changes its name to Meta", "2021-10-28",
    "The company formerly known as Facebook, Inc. has changed its corporate name to Meta Platforms, Inc. Meta is now the parent company of the Facebook app, Instagram, WhatsApp and Messenger. This announcement supersedes earlier corporate naming.")

rev("sw-java-cadence", "software",
    "How often are new feature releases of the Java Development Kit (JDK) published?",
    "roughly every two to three years", ["two to three years", "2-3 years", "every few years", "several years"],
    "every six months", ["six months", "6 months", "twice a year"],
    "Java SE release model", "2016-05-20",
    "Major releases of Java SE are feature-driven and ship roughly every two to three years, after all planned features are complete. Java SE 8 shipped in 2014 and Java SE 9 is planned for a later date once its major features are finished.",
    "Faster, time-based Java release cadence announced", "2017-09-21",
    "Beginning with JDK 10, Java will move to a strict time-based release model with a new feature release every six months, in March and September. Long-term support releases will be designated every few years. This supersedes the previous feature-driven multi-year cadence.")

rev("sw-angularjs", "software",
    "Is AngularJS (Angular 1.x) still receiving official support from the Angular team?",
    "yes, AngularJS is in long-term support", ["yes", "long-term support", "long term support", "lts", "supported"],
    "no, AngularJS support has ended", ["ended", "no longer", "end of life", "not supported", "discontinued", "unsupported"],
    "AngularJS long-term support", "2019-07-01",
    "AngularJS is in a long-term support period. During this period the team publishes releases that fix security issues, browser compatibility problems and incompatibilities with jQuery updates. Applications on AngularJS remain supported.",
    "AngularJS long-term support ends", "2022-01-01",
    "The long-term support period for AngularJS has ended. The Angular team no longer publishes updates, security fixes or releases for AngularJS. Users are advised to migrate to Angular. This supersedes earlier support commitments.")

rev("sw-ubuntu-desktop", "software",
    "What is the default desktop environment of Ubuntu?",
    "Unity", ["unity"],
    "GNOME", ["gnome"],
    "Ubuntu desktop overview", "2016-04-21",
    "Ubuntu ships with Unity as its default desktop environment. Unity, developed by Canonical, features a launcher on the left side of the screen and a top panel with global menus.",
    "Ubuntu 17.10 released with GNOME as the default desktop", "2017-10-19",
    "Ubuntu now uses GNOME as its default desktop environment. Canonical has discontinued development of Unity and all new Ubuntu desktop releases ship with GNOME Shell. This supersedes earlier documentation describing Unity as the default.")

rev("sw-ie11", "software",
    "Is Internet Explorer 11 a supported Microsoft web browser?",
    "yes, Internet Explorer 11 is supported", ["yes", "supported", "continues to be supported"],
    "no, Internet Explorer 11 has been retired", ["retired", "no longer supported", "not supported", "end of support", "discontinued", "disabled"],
    "Internet Explorer 11 support lifecycle", "2019-03-05",
    "Internet Explorer 11 is a supported component of Windows and continues to receive security updates through Windows Update. Organisations may continue to deploy Internet Explorer 11 for legacy web applications.",
    "Internet Explorer 11 desktop application retired", "2022-06-15",
    "The Internet Explorer 11 desktop application is retired and out of support. Users are redirected to Microsoft Edge, which includes an Internet Explorer mode for legacy sites. This notice supersedes previous lifecycle guidance for Internet Explorer 11.")

rev("sw-docker-desktop", "software",
    "Is Docker Desktop free to use inside large companies with more than 250 employees or more than 10 million dollars in revenue?",
    "yes, Docker Desktop is free for all users", ["yes", "free for all", "free to use", "no charge", "free of charge"],
    "no, large companies need a paid subscription", ["paid", "subscription", "requires a license", "requires a licence", "not free", "no longer free"],
    "Docker Desktop licensing", "2020-08-10",
    "Docker Desktop is available free of charge for all users, including individuals, small businesses and large enterprises. There is no licensing fee for commercial use.",
    "Docker Desktop subscription requirement for large organisations", "2022-01-31",
    "Docker Desktop now requires a paid Docker subscription for professional use in organisations with more than 250 employees or more than 10 million US dollars in annual revenue. It remains free for personal use, education, non-commercial open source projects and small businesses. This supersedes earlier free-for-all licensing.",
    new_effective="2022-01-31")

rev("sw-react-hooks", "software",
    "What is the recommended way to use state and lifecycle features in React function components?",
    "it is not possible; class components must be used for state and lifecycle", ["not possible", "class component", "cannot", "must use class", "only class"],
    "React Hooks such as useState and useEffect", ["hook", "usestate", "useeffect"],
    "React components: function versus class", "2018-06-12",
    "Function components in React are stateless. If a component needs local state or lifecycle methods, it must be written as a class component extending React.Component. There is no way to use state inside a function component.",
    "Introducing Hooks in React 16.8", "2019-02-06",
    "React 16.8 introduces Hooks. Hooks such as useState and useEffect let function components use state and other React features without writing a class. Hooks are now the recommended approach for new components. This supersedes earlier guidance that state requires class components.")

rev("sw-centos8", "software",
    "Is CentOS Linux 8 still receiving updates?",
    "yes, CentOS Linux 8 is supported", ["yes", "supported", "receives updates", "receiving updates"],
    "no, CentOS Linux 8 has reached end of life", ["end of life", "eol", "no longer", "ended", "discontinued", "not supported"],
    "CentOS Linux 8 lifecycle", "2020-05-18",
    "CentOS Linux 8 is a community rebuild of Red Hat Enterprise Linux 8 and receives security and bug-fix updates as a supported distribution for production servers.",
    "CentOS Linux 8 end of life", "2021-12-31",
    "CentOS Linux 8 has reached its end of life and no longer receives updates of any kind. The project has shifted to CentOS Stream. Users should migrate to CentOS Stream or another distribution. This supersedes earlier lifecycle statements.",
    undated_old=True)

rev("sw-tls", "software",
    "Are TLS 1.0 and TLS 1.1 approved protocol versions according to the IETF?",
    "yes, they remain valid protocol versions", ["yes", "valid", "approved", "may be used", "acceptable", "remain"],
    "no, TLS 1.0 and TLS 1.1 are formally deprecated", ["deprecated", "must not", "should not", "no longer", "obsolete", "not approved"],
    "TLS protocol versions in use", "2017-02-20",
    "TLS 1.0, TLS 1.1 and TLS 1.2 are all valid published versions of the Transport Layer Security protocol. Servers commonly support all three versions for compatibility.",
    "RFC 8996: Deprecating TLS 1.0 and TLS 1.1", "2021-03-23",
    "The IETF has formally deprecated TLS 1.0 and TLS 1.1. These versions must not be used, and implementations should negotiate only TLS 1.2 or later. This document supersedes earlier guidance permitting these versions.")

rev("sw-bitcoin-halving", "software",
    "What is the current Bitcoin block subsidy (block reward) paid to miners per block?",
    "6.25 BTC", ["6.25"],
    "3.125 BTC", ["3.125"],
    "Bitcoin mining rewards after the third halving", "2020-05-11",
    "Following the third halving, the Bitcoin block subsidy is 6.25 BTC per block. Miners receive this subsidy plus transaction fees for each block they add to the chain.",
    "Fourth Bitcoin halving completed", "2024-04-20",
    "The fourth Bitcoin halving has occurred at block 840,000. The block subsidy has been reduced from 6.25 BTC to 3.125 BTC per block. This supersedes the previous reward schedule.")

rev("sw-ga4", "software",
    "Which Google Analytics property type should be used to collect website data?",
    "Universal Analytics", ["universal analytics", "ua"],
    "Google Analytics 4 (GA4)", ["ga4", "analytics 4"],
    "Setting up Google Analytics for your website", "2019-09-03",
    "To measure traffic on a website, create a Universal Analytics property in Google Analytics and add the tracking code to every page. Universal Analytics is the standard property type for websites.",
    "Universal Analytics has stopped processing data", "2023-07-01",
    "Standard Universal Analytics properties have stopped processing new data. All website measurement must now use Google Analytics 4 properties. This supersedes earlier setup guidance based on Universal Analytics.",
    new_effective="2023-07-01")

rev("sw-windows10", "software",
    "Is Windows 10 still under mainstream support with free security updates from Microsoft?",
    "yes, Windows 10 is supported", ["yes", "supported", "receives security updates", "receiving security updates"],
    "no, Windows 10 has reached end of support", ["end of support", "no longer", "ended", "not supported", "unsupported", "reached the end"],
    "Windows 10 lifecycle", "2022-02-14",
    "Windows 10 is a supported operating system. Microsoft provides free monthly security and quality updates to all supported editions of Windows 10 through Windows Update.",
    "Windows 10 reaches end of support", "2025-10-14",
    "Windows 10 has reached the end of support. Microsoft no longer provides free security updates, feature updates or technical support for Windows 10. Users should upgrade to Windows 11 or enrol in the paid Extended Security Updates programme. This supersedes previous lifecycle guidance.")

rev("sw-tweet-length", "software",
    "What is the character limit of a standard post for regular users on Twitter/X?",
    "140 characters", ["140"],
    "280 characters", ["280"],
    "Composing a tweet", "2016-03-08",
    "Tweets are limited to 140 characters. If your message is longer, you must shorten it or split it across several tweets.",
    "Twitter doubles the character limit to 280", "2017-11-07",
    "The character limit for tweets has been raised from 140 to 280 characters for all users in most languages. This supersedes the earlier 140-character limit.")

rev("sw-iphone-port", "software",
    "What charging connector do the latest iPhone models use?",
    "the Lightning connector", ["lightning"],
    "USB-C", ["usb-c", "usb c", "usb type-c", "type-c"],
    "iPhone charging and connectivity", "2022-09-16",
    "All current iPhone models charge and connect to accessories through Apple's proprietary Lightning port. A Lightning to USB cable is included with the phone.",
    "iPhone 15 adopts USB-C", "2023-09-12",
    "The newly announced iPhone 15 line replaces the Lightning port with a USB-C connector for charging and data transfer. All subsequent iPhone models use USB-C. This supersedes earlier documentation of the Lightning connector.")

rev("sw-macos-shell", "software",
    "What is the default login shell in macOS?",
    "bash", ["bash"],
    "zsh", ["zsh", "z shell"],
    "Using the Terminal in macOS", "2018-10-01",
    "When you open Terminal in macOS, a bash shell starts by default. bash is the default login shell for all user accounts on macOS.",
    "macOS Catalina makes zsh the default shell", "2019-10-07",
    "Starting with macOS Catalina, zsh is the default login shell for new user accounts. bash remains available but is no longer the default. This supersedes earlier documentation describing bash as the default.")

rev("sw-flash", "software",
    "Is Adobe Flash Player still supported by Adobe?",
    "yes, Flash Player is supported", ["yes", "supported", "continues to"],
    "no, Flash Player has reached end of life", ["end of life", "eol", "no longer", "discontinued", "not supported", "ended"],
    "Adobe Flash Player support", "2016-05-02",
    "Adobe continues to support and update Flash Player with regular security releases for all major browsers and operating systems.",
    "Adobe Flash Player end of life", "2020-12-31",
    "Adobe Flash Player has reached end of life. Adobe no longer supports Flash Player and blocks Flash content from running. Users should uninstall Flash Player. This supersedes earlier support statements.",
    undated_old=True)

rev("sw-java-lts", "software",
    "What is the most recent long-term-support (LTS) release of Java?",
    "Java 21", ["java 21", "jdk 21", "21"],
    "Java 25", ["java 25", "jdk 25", "25"],
    "JDK 21 released as the new LTS version", "2023-09-19",
    "JDK 21 is now generally available and is the latest long-term-support release of Java, succeeding JDK 17. Oracle will provide extended support for JDK 21 for several years.",
    "JDK 25 released as the new LTS version", "2025-09-16",
    "JDK 25 is now generally available and is designated the newest long-term-support release of Java, succeeding JDK 21 as the current LTS. This supersedes the earlier LTS designation.")

rev("sw-gdpr", "policy",
    "Which European Union data protection law is currently in force?",
    "the Data Protection Directive 95/46/EC", ["directive", "95/46"],
    "the General Data Protection Regulation (GDPR)", ["gdpr", "general data protection regulation", "2016/679"],
    "EU data protection framework", "2016-01-20",
    "Data protection in the European Union is governed by Directive 95/46/EC, which each member state implements through its own national legislation.",
    "GDPR becomes applicable across the EU", "2018-05-25",
    "The General Data Protection Regulation (EU) 2016/679 now applies directly in all EU member states and repeals Directive 95/46/EC. This supersedes the previous directive-based framework.",
    new_effective="2018-05-25")

# --------------------------------------------------------------------------------------
# INDIAN LAW AND POLICY
# --------------------------------------------------------------------------------------
rev("in-ipc", "law",
    "Which statute is India's principal criminal code defining offences and their punishments?",
    "the Indian Penal Code, 1860", ["indian penal code", "ipc"],
    "the Bharatiya Nyaya Sanhita, 2023", ["bharatiya nyaya sanhita", "bns"],
    "Overview of criminal law in India", "2021-08-10",
    "The Indian Penal Code, 1860 is the principal criminal code of India. It defines offences and prescribes punishments, and it is applied together with the Code of Criminal Procedure and the Indian Evidence Act.",
    "New criminal laws come into force", "2024-07-01",
    "The Bharatiya Nyaya Sanhita, 2023 has come into force and replaces the Indian Penal Code, 1860 as India's principal criminal code. The Bharatiya Nagarik Suraksha Sanhita and the Bharatiya Sakshya Adhiniyam replace the Code of Criminal Procedure and the Indian Evidence Act respectively. This supersedes the earlier statutes.",
    new_effective="2024-07-01")

rev("in-evidence", "law",
    "Which statute governs the law of evidence in Indian courts?",
    "the Indian Evidence Act, 1872", ["indian evidence act", "evidence act, 1872", "evidence act 1872"],
    "the Bharatiya Sakshya Adhiniyam, 2023", ["bharatiya sakshya", "bsa"],
    "Law of evidence in India: a primer", "2020-02-03",
    "The admissibility and relevance of evidence in Indian courts is governed by the Indian Evidence Act, 1872, which applies to all judicial proceedings in India.",
    "Bharatiya Sakshya Adhiniyam replaces the Indian Evidence Act", "2024-07-01",
    "The Bharatiya Sakshya Adhiniyam, 2023 is now in force and replaces the Indian Evidence Act, 1872 as the law governing evidence in Indian courts. This supersedes the earlier Act.",
    new_effective="2024-07-01", undated_old=True)

rev("in-377", "law",
    "Is consensual sexual activity between adults of the same sex a criminal offence in India?",
    "yes, it is an offence under Section 377 of the Indian Penal Code", ["yes", "offence", "criminal", "punishable", "illegal"],
    "no, it has been decriminalised", ["decriminalised", "decriminalized", "not a crime", "not an offence", "no longer", "legal", "struck down"],
    "Section 377 of the Indian Penal Code", "2016-11-15",
    "Section 377 of the Indian Penal Code criminalises carnal intercourse against the order of nature and, as upheld by the Supreme Court, applies to consensual sexual activity between adults of the same sex, which is therefore a punishable offence.",
    "Supreme Court judgment in Navtej Singh Johar v. Union of India", "2018-09-06",
    "A Constitution Bench of the Supreme Court has held that Section 377, in so far as it criminalises consensual sexual conduct between adults of the same sex, is unconstitutional. Such conduct is no longer a criminal offence. This judgment supersedes the earlier position.")

rev("in-triple-talaq", "law",
    "Is pronouncing instant triple talaq (talaq-e-biddat) a criminal offence in India?",
    "no, it is not a criminal offence", ["no", "not a criminal", "not an offence", "not criminal", "civil"],
    "yes, it is a criminal offence punishable with imprisonment", ["yes", "criminal offence", "punishable", "imprisonment", "offence", "illegal"],
    "Legal status of talaq-e-biddat", "2017-10-10",
    "Although the Supreme Court has declared instant triple talaq invalid as a means of divorce, pronouncing it is not a criminal offence under any statute, and no penal consequences attach to the husband.",
    "The Muslim Women (Protection of Rights on Marriage) Act, 2019", "2019-07-31",
    "The Act makes the pronouncement of instant triple talaq by a Muslim husband void and illegal, and a cognisable offence punishable with imprisonment of up to three years and a fine. This supersedes the earlier position that no penal consequences attached.",
    new_effective="2019-07-31")

rev("in-article370", "law",
    "Does Jammu and Kashmir have special autonomous status under Article 370 of the Indian Constitution?",
    "yes, it has special status under Article 370", ["yes", "special status", "autonomous", "has special"],
    "no, the special status has been revoked", ["revoked", "abrogated", "no longer", "removed", "withdrawn", "ceased"],
    "Article 370 and the status of Jammu and Kashmir", "2018-04-09",
    "Under Article 370 of the Constitution, the State of Jammu and Kashmir enjoys special autonomous status. Parliament's power to make laws for the state is limited, and the state has its own constitution.",
    "Presidential order revokes the special status of Jammu and Kashmir", "2019-08-05",
    "By Presidential order, the special status conferred on Jammu and Kashmir under Article 370 has been revoked, and all provisions of the Constitution of India now apply to the territory. The State is being reorganised into two Union Territories. This supersedes the earlier constitutional position.")

rev("in-niti", "policy",
    "Which institution serves as the Government of India's apex policy planning body?",
    "the Planning Commission", ["planning commission"],
    "NITI Aayog", ["niti aayog", "niti"],
    "The Planning Commission of India", "2013-07-22",
    "The Planning Commission is the Government of India's apex body for formulating Five-Year Plans and allocating plan funds to states and central ministries. It is chaired by the Prime Minister.",
    "NITI Aayog replaces the Planning Commission", "2015-01-01",
    "The Government of India has established NITI Aayog (National Institution for Transforming India) as its policy think tank, replacing the Planning Commission. NITI Aayog is now the apex policy body. This supersedes the earlier arrangement.")

rev("in-tax-regime", "policy",
    "Which income tax regime is the default for individual taxpayers in India?",
    "the old tax regime with deductions and exemptions", ["old regime", "old tax regime", "existing regime", "regular regime", "with deductions"],
    "the new tax regime with concessional rates", ["new regime", "new tax regime", "concessional", "115bac"],
    "Choosing between the old and new income tax regimes", "2021-06-15",
    "Individual taxpayers in India are assessed under the old tax regime by default, which allows deductions and exemptions. Taxpayers may opt into the new concessional tax regime under section 115BAC if they wish.",
    "New tax regime becomes the default", "2023-04-01",
    "The new concessional income tax regime under section 115BAC is now the default regime for individual taxpayers. Those who wish to claim deductions under the old regime must opt out of the new regime. This supersedes the earlier default.",
    new_effective="2023-04-01")

rev("in-president", "politics",
    "Who is the President of India?",
    "Ram Nath Kovind", ["kovind"],
    "Droupadi Murmu", ["murmu"],
    "The President of India", "2021-01-26",
    "Ram Nath Kovind is the President of India, the constitutional head of state. He assumed office as the fourteenth President.",
    "Droupadi Murmu sworn in as President of India", "2022-07-25",
    "Droupadi Murmu has been sworn in as the fifteenth President of India, succeeding Ram Nath Kovind. This supersedes earlier records of the office holder.")

rev("in-gst-gaming", "policy",
    "What GST rate applies to online money gaming in India?",
    "18 percent on the platform fee", ["18"],
    "28 percent on the full face value of bets", ["28"],
    "GST treatment of online gaming", "2022-03-14",
    "Online gaming platforms in India pay Goods and Services Tax at 18 percent on the platform fee or gross gaming revenue they retain, not on the total amount staked by players.",
    "28 percent GST on online money gaming comes into effect", "2023-10-01",
    "Online money gaming, casinos and horse racing are now taxed at 28 percent GST on the full face value of bets or deposits, following amendments to the GST laws. This supersedes the earlier 18 percent treatment.",
    new_effective="2023-10-01")

rev("in-gst-insurance", "policy",
    "What GST rate applies to individual health insurance premiums in India?",
    "18 percent", ["18"],
    "nil, individual health insurance is exempt from GST", ["nil", "exempt", "zero", "0 percent", "0%", "no gst"],
    "GST on insurance premiums", "2024-02-05",
    "Premiums paid for individual health insurance and life insurance policies in India attract Goods and Services Tax at the standard rate of 18 percent.",
    "GST exemption on individual life and health insurance", "2025-09-22",
    "Individual life insurance and individual health insurance policies, including family floater and senior citizen policies, are now exempt from GST. The earlier 18 percent levy no longer applies. This supersedes the earlier treatment.",
    new_effective="2025-09-22")

rev("in-gst-slabs", "policy",
    "What are the main GST rate slabs in India?",
    "four slabs of 5, 12, 18 and 28 percent", ["12", "four slabs", "four-tier", "4 slabs"],
    "two main slabs of 5 and 18 percent, with a 40 percent rate for luxury and sin goods", ["two slabs", "two-tier", "two main", "40", "5 and 18", "5% and 18%"],
    "Structure of GST rates in India", "2023-01-09",
    "Goods and services in India are taxed under four main GST slabs of 5 percent, 12 percent, 18 percent and 28 percent, with a compensation cess on certain luxury and demerit goods.",
    "Rationalised two-rate GST structure takes effect", "2025-09-22",
    "The GST rate structure has been rationalised into two main slabs of 5 percent and 18 percent. The 12 percent and 28 percent slabs have been abolished, and a special 40 percent rate applies to luxury and sin goods. This supersedes the earlier four-slab structure.",
    new_effective="2025-09-22")

rev("in-uts", "policy",
    "How many Union Territories does India have?",
    "7", ["seven", "7"],
    "8", ["eight", "8"],
    "States and Union Territories of India", "2018-03-12",
    "India is a union of 29 states and 7 union territories. The union territories are administered by the central government through administrators or lieutenant governors.",
    "Merger of Dadra and Nagar Haveli with Daman and Diu", "2020-01-26",
    "Following the reorganisation of Jammu and Kashmir into two union territories and the merger of Dadra and Nagar Haveli with Daman and Diu into a single union territory, India now has 28 states and 8 union territories. This supersedes earlier counts.",
    t_past="2019-01-15")

rev("in-5g", "policy",
    "Are commercial 5G mobile services available in India?",
    "no, 5G has not been launched", ["no", "not yet", "not launched", "not available", "has not"],
    "yes, commercial 5G services have been launched", ["yes", "launched", "available", "rolled out"],
    "Status of 5G in India", "2021-11-02",
    "Commercial 5G services are not yet available in India. Spectrum auctions have not been completed and telecom operators are conducting trials only.",
    "Commercial 5G services launched in India", "2022-10-01",
    "The Prime Minister has formally launched commercial 5G services in India. Telecom operators are rolling out 5G networks in major cities. This supersedes earlier statements that 5G was unavailable.",
    undated_old=True)

rev("in-isro", "politics",
    "Who is the Chairman of ISRO?",
    "S. Somanath", ["somanath"],
    "V. Narayanan", ["narayanan"],
    "ISRO leadership", "2023-08-24",
    "S. Somanath is the Chairman of the Indian Space Research Organisation and Secretary of the Department of Space.",
    "V. Narayanan takes over as ISRO Chairman", "2025-01-14",
    "V. Narayanan has assumed charge as Chairman of ISRO and Secretary of the Department of Space, succeeding S. Somanath. This supersedes earlier leadership records.")

rev("in-rbi", "politics",
    "Who is the Governor of the Reserve Bank of India?",
    "Shaktikanta Das", ["shaktikanta", "das"],
    "Sanjay Malhotra", ["malhotra"],
    "Governor of the Reserve Bank of India", "2023-05-02",
    "Shaktikanta Das is the Governor of the Reserve Bank of India, the country's central bank.",
    "Sanjay Malhotra assumes office as RBI Governor", "2024-12-11",
    "Sanjay Malhotra has taken charge as the twenty-sixth Governor of the Reserve Bank of India, succeeding Shaktikanta Das. This supersedes earlier records.")

rev("in-delhi-cm", "politics",
    "Who is the Chief Minister of Delhi?",
    "Atishi", ["atishi"],
    "Rekha Gupta", ["rekha gupta", "gupta"],
    "Atishi sworn in as Chief Minister of Delhi", "2024-09-21",
    "Atishi has been sworn in as the Chief Minister of Delhi, succeeding Arvind Kejriwal.",
    "Rekha Gupta sworn in as Chief Minister of Delhi", "2025-02-20",
    "Rekha Gupta has been sworn in as the Chief Minister of Delhi following the assembly election. She succeeds Atishi. This supersedes earlier records.")

rev("in-vp", "politics",
    "Who is the Vice President of India?",
    "Jagdeep Dhankhar", ["dhankhar"],
    "C. P. Radhakrishnan", ["radhakrishnan"],
    "The Vice President of India", "2024-03-05",
    "Jagdeep Dhankhar is the Vice President of India and ex officio Chairman of the Rajya Sabha.",
    "C. P. Radhakrishnan sworn in as Vice President", "2025-09-12",
    "C. P. Radhakrishnan has been sworn in as the Vice President of India following the resignation of Jagdeep Dhankhar. This supersedes earlier records.")

rev("in-prayagraj", "policy",
    "What is the official name of the Uttar Pradesh city formerly known as Allahabad?",
    "Allahabad", ["allahabad"],
    "Prayagraj", ["prayagraj"],
    "District profile: Allahabad", "2017-05-30",
    "Allahabad is a major city and district headquarters in Uttar Pradesh, located at the confluence of the Ganga and Yamuna rivers. The city's official name is Allahabad.",
    "Allahabad officially renamed Prayagraj", "2018-10-16",
    "The Uttar Pradesh government has officially renamed the city and district of Allahabad as Prayagraj. All official records now use the name Prayagraj. This supersedes the earlier name.")

rev("in-sambhajinagar", "policy",
    "What is the official name of the Maharashtra city formerly known as Aurangabad?",
    "Aurangabad", ["aurangabad"],
    "Chhatrapati Sambhajinagar", ["sambhajinagar", "sambhaji nagar"],
    "District profile: Aurangabad", "2021-04-12",
    "Aurangabad is a city and district headquarters in Maharashtra, known for the nearby Ajanta and Ellora caves. Its official name is Aurangabad.",
    "Aurangabad renamed Chhatrapati Sambhajinagar", "2023-02-24",
    "The Union Home Ministry has approved the renaming of Aurangabad city and district in Maharashtra as Chhatrapati Sambhajinagar. Official records now use the new name. This supersedes the earlier name.")

rev("in-air-india", "business",
    "Who owns Air India?",
    "the Government of India", ["government of india", "government", "state-owned", "state owned", "public sector"],
    "the Tata Group", ["tata"],
    "Air India corporate profile", "2020-07-07",
    "Air India is the flag carrier airline of India, wholly owned by the Government of India through the Ministry of Civil Aviation.",
    "Air India handed over to the Tata Group", "2022-01-27",
    "The Government of India has completed the strategic disinvestment of Air India, transferring full ownership to Talace Private Limited, a subsidiary of Tata Sons. Air India is now owned by the Tata Group. This supersedes earlier ownership records.")

rev("in-ipl-teams", "sports",
    "How many teams compete in the Indian Premier League (IPL)?",
    "8", ["eight", "8"],
    "10", ["ten", "10"],
    "About the Indian Premier League", "2020-09-19",
    "The Indian Premier League is a professional Twenty20 cricket league contested by eight franchise teams representing Indian cities.",
    "IPL expands to ten teams", "2022-03-26",
    "With the addition of the Gujarat Titans and the Lucknow Super Giants, the Indian Premier League is now contested by ten franchise teams. This supersedes earlier descriptions of an eight-team league.")

# --------------------------------------------------------------------------------------
# WORLD POLITICS AND GEOGRAPHY
# --------------------------------------------------------------------------------------
rev("wd-uk-monarch", "politics",
    "Who is the reigning monarch of the United Kingdom?",
    "Queen Elizabeth II", ["elizabeth"],
    "King Charles III", ["charles"],
    "The British monarchy", "2021-06-02",
    "Queen Elizabeth II is the reigning monarch of the United Kingdom and the other Commonwealth realms, having acceded to the throne in 1952.",
    "Accession of King Charles III", "2022-09-08",
    "Following the death of Queen Elizabeth II, her son has acceded to the throne as King Charles III and is now the reigning monarch of the United Kingdom. This supersedes earlier records.")

rev("wd-nato", "politics",
    "Which country is the most recent to join NATO?",
    "Finland", ["finland"],
    "Sweden", ["sweden"],
    "Finland joins NATO", "2023-04-04",
    "Finland has formally joined the North Atlantic Treaty Organization as its thirty-first member, becoming the newest member of the alliance.",
    "Sweden joins NATO as the thirty-second member", "2024-03-07",
    "Sweden has formally become the thirty-second member of NATO and is now the alliance's most recent member, following Finland. This supersedes earlier records.")

rev("wd-turkiye", "politics",
    "What is the official name of the Republic of Turkey as registered at the United Nations?",
    "Turkey", ["turkey"],
    "Türkiye", ["türkiye", "turkiye"],
    "Member states of the United Nations: Turkey", "2020-10-05",
    "The Republic of Turkey is listed at the United Nations under the name Turkey, a founding member of the organisation.",
    "United Nations registers the name Türkiye", "2022-06-01",
    "The United Nations has accepted the request of the Republic of Türkiye to change its registered name from Turkey to Türkiye in all official documents. This supersedes the earlier name.")

rev("wd-north-macedonia", "politics",
    "What is the official name of the country formerly known as the Former Yugoslav Republic of Macedonia?",
    "the Republic of Macedonia (Former Yugoslav Republic of Macedonia)", ["republic of macedonia", "former yugoslav", "fyrom", "macedonia"],
    "the Republic of North Macedonia", ["north macedonia"],
    "Country profile: Macedonia", "2017-09-11",
    "The country is known constitutionally as the Republic of Macedonia and is referred to in the United Nations as the Former Yugoslav Republic of Macedonia because of a naming dispute with Greece.",
    "Prespa agreement enters into force: Republic of North Macedonia", "2019-02-12",
    "Under the Prespa agreement with Greece, the country has officially changed its name to the Republic of North Macedonia. This supersedes the earlier names.")

rev("wd-eswatini", "politics",
    "What is the official name of the southern African kingdom formerly called Swaziland?",
    "the Kingdom of Swaziland", ["swaziland"],
    "the Kingdom of Eswatini", ["eswatini"],
    "Country profile: Swaziland", "2016-08-01",
    "The Kingdom of Swaziland is a landlocked monarchy in southern Africa, bordered by South Africa and Mozambique.",
    "Swaziland officially renamed the Kingdom of Eswatini", "2018-04-19",
    "The King has announced that the country's official name is changed from the Kingdom of Swaziland to the Kingdom of Eswatini. This supersedes the earlier name.")

rev("wd-brexit", "politics",
    "Is the United Kingdom a member state of the European Union?",
    "yes", ["yes", "is a member", "member state"],
    "no, the United Kingdom has left the European Union", ["no", "left", "no longer", "withdrawn", "not a member", "former member"],
    "Member states of the European Union", "2018-06-11",
    "The United Kingdom is one of the 28 member states of the European Union, having joined the European Communities in 1973.",
    "United Kingdom withdraws from the European Union", "2020-01-31",
    "The United Kingdom has formally withdrawn from the European Union and is no longer a member state. The Union now has 27 members. This supersedes earlier membership lists.")

rev("wd-croatia-euro", "politics",
    "What is the official currency of Croatia?",
    "the Croatian kuna", ["kuna"],
    "the euro", ["euro"],
    "Currency of Croatia", "2021-05-17",
    "The official currency of Croatia is the Croatian kuna, which is divided into 100 lipa.",
    "Croatia adopts the euro", "2023-01-01",
    "Croatia has adopted the euro as its official currency, replacing the kuna, and has become the twentieth member of the euro area. This supersedes earlier currency information.",
    undated_old=True)

rev("wd-population", "politics",
    "Which country has the largest population in the world?",
    "China", ["china"],
    "India", ["india"],
    "World population rankings", "2021-07-11",
    "China is the most populous country in the world with over 1.4 billion people, followed by India.",
    "India overtakes China as the world's most populous country", "2023-04-24",
    "According to United Nations estimates, India has surpassed China to become the most populous country in the world. This supersedes earlier rankings.")

rev("wd-astana", "politics",
    "What is the name of the capital city of Kazakhstan?",
    "Nur-Sultan", ["nur-sultan", "nursultan", "nur sultan"],
    "Astana", ["astana"],
    "Capital of Kazakhstan renamed Nur-Sultan", "2019-03-23",
    "The capital of Kazakhstan, previously called Astana, has been renamed Nur-Sultan in honour of the country's first president. The official name of the capital is Nur-Sultan.",
    "Kazakhstan restores the name Astana for its capital", "2022-09-17",
    "The capital of Kazakhstan has been renamed back to Astana. The name Nur-Sultan is no longer in official use. This supersedes the earlier renaming.")

rev("wd-us-president", "politics",
    "Who is the President of the United States?",
    "Joe Biden", ["biden"],
    "Donald Trump", ["trump"],
    "President of the United States", "2023-03-01",
    "Joe Biden is the forty-sixth President of the United States, having taken office in January 2021.",
    "Donald Trump inaugurated as the forty-seventh President", "2025-01-20",
    "Donald Trump has been inaugurated as the forty-seventh President of the United States, succeeding Joe Biden. This supersedes earlier records.")

rev("wd-canada-pm", "politics",
    "Who is the Prime Minister of Canada?",
    "Justin Trudeau", ["trudeau"],
    "Mark Carney", ["carney"],
    "Prime Minister of Canada", "2024-05-06",
    "Justin Trudeau is the Prime Minister of Canada and leader of the Liberal Party.",
    "Mark Carney sworn in as Prime Minister of Canada", "2025-03-14",
    "Mark Carney has been sworn in as the twenty-fourth Prime Minister of Canada, succeeding Justin Trudeau. This supersedes earlier records.")

rev("wd-germany", "politics",
    "Who is the Chancellor of Germany?",
    "Olaf Scholz", ["scholz"],
    "Friedrich Merz", ["merz"],
    "Chancellor of Germany", "2024-02-19",
    "Olaf Scholz is the Federal Chancellor of Germany, leading a coalition government.",
    "Friedrich Merz elected Chancellor", "2025-05-06",
    "The Bundestag has elected Friedrich Merz as Federal Chancellor of Germany, succeeding Olaf Scholz. This supersedes earlier records.")

rev("wd-uk-pm", "politics",
    "Who is the Prime Minister of the United Kingdom?",
    "Rishi Sunak", ["sunak"],
    "Keir Starmer", ["starmer"],
    "Prime Minister of the United Kingdom", "2023-11-13",
    "Rishi Sunak is the Prime Minister of the United Kingdom and leader of the Conservative Party.",
    "Keir Starmer appointed Prime Minister", "2024-07-05",
    "Following the general election, Keir Starmer has been appointed Prime Minister of the United Kingdom, succeeding Rishi Sunak. This supersedes earlier records.")

rev("wd-pope", "politics",
    "Who is the Pope, head of the Catholic Church?",
    "Pope Francis", ["francis"],
    "Pope Leo XIV", ["leo"],
    "The Pope", "2024-08-15",
    "Pope Francis is the head of the Catholic Church and sovereign of the Vatican City State, having been elected in 2013.",
    "Election of Pope Leo XIV", "2025-05-08",
    "The conclave has elected Cardinal Robert Prevost as Pope, who has taken the name Leo XIV, succeeding Pope Francis. This supersedes earlier records.")

rev("wd-syria", "politics",
    "Who is the President of Syria?",
    "Bashar al-Assad", ["assad"],
    "Ahmed al-Sharaa", ["sharaa", "al-shara", "jolani", "julani"],
    "Government of Syria", "2024-06-03",
    "Bashar al-Assad is the President of Syria, an office he has held since 2000.",
    "Ahmed al-Sharaa named President of Syria for the transitional period", "2025-01-29",
    "Following the fall of the Assad government, Ahmed al-Sharaa has been declared President of Syria for the transitional period. This supersedes earlier records.")

# --------------------------------------------------------------------------------------
# MEDICINE AND PUBLIC HEALTH
# --------------------------------------------------------------------------------------
rev("md-pheic", "medicine",
    "Is COVID-19 currently a Public Health Emergency of International Concern (PHEIC) according to the WHO?",
    "yes", ["yes", "remains a", "is a public health emergency", "continues to"],
    "no, the PHEIC has been ended", ["no", "no longer", "ended", "lifted", "not a public health emergency", "declared over"],
    "WHO statement on the COVID-19 emergency", "2022-01-19",
    "The Director-General of the WHO has determined that the COVID-19 pandemic continues to constitute a Public Health Emergency of International Concern.",
    "WHO declares an end to COVID-19 as a global health emergency", "2023-05-05",
    "The WHO Director-General has declared that COVID-19 no longer constitutes a Public Health Emergency of International Concern. This supersedes earlier determinations.")

rev("md-aspirin", "medicine",
    "Does the US Preventive Services Task Force recommend starting low-dose aspirin for primary prevention of cardiovascular disease in adults aged 60 years or older?",
    "it may be considered as an individual decision for some adults aged 60 to 69 at elevated risk", ["individual", "may be considered", "selectively", "case-by-case", "some adults"],
    "no, it recommends against initiating aspirin in adults aged 60 or older", ["against", "not recommend", "should not", "does not recommend", "recommends against"],
    "USPSTF recommendation: aspirin for the primary prevention of cardiovascular disease", "2016-04-12",
    "The Task Force concludes that for adults aged 60 to 69 years with a 10 percent or greater 10-year cardiovascular risk, the decision to initiate low-dose aspirin should be an individual one. Evidence is insufficient for adults aged 70 and older.",
    "USPSTF final recommendation: aspirin use to prevent cardiovascular disease", "2022-04-26",
    "The Task Force recommends against initiating low-dose aspirin for the primary prevention of cardiovascular disease in adults aged 60 years or older. This recommendation supersedes the 2016 statement.")

rev("md-hypertension", "medicine",
    "At what blood pressure threshold is stage 1 hypertension diagnosed under the American College of Cardiology and American Heart Association guideline?",
    "140/90 mm Hg or higher", ["140/90", "140 over 90", "140"],
    "130/80 mm Hg or higher", ["130/80", "130 over 80", "130"],
    "Blood pressure classification for adults", "2014-02-05",
    "Hypertension in adults is defined as a systolic blood pressure of 140 mm Hg or higher or a diastolic pressure of 90 mm Hg or higher. Readings between 120/80 and 139/89 are classified as prehypertension.",
    "ACC/AHA high blood pressure clinical practice guideline", "2017-11-13",
    "The new guideline defines stage 1 hypertension as a systolic pressure of 130 to 139 mm Hg or a diastolic pressure of 80 to 89 mm Hg. The former category of prehypertension is eliminated. This guideline supersedes the earlier 140/90 threshold.")

rev("md-crc-screening", "medicine",
    "At what age does the US Preventive Services Task Force recommend that adults at average risk begin colorectal cancer screening?",
    "age 50", ["50", "fifty"],
    "age 45", ["45", "forty-five"],
    "USPSTF recommendation: screening for colorectal cancer", "2016-06-15",
    "The Task Force recommends screening for colorectal cancer starting at age 50 years and continuing until age 75 years in adults at average risk.",
    "USPSTF updated recommendation: colorectal cancer screening", "2021-05-18",
    "The Task Force now recommends that adults at average risk begin screening for colorectal cancer at age 45 years. This supersedes the 2016 recommendation to start at age 50.")

rev("md-peanut", "medicine",
    "When should peanut-containing foods be introduced to infants at high risk of peanut allergy, according to US guidelines?",
    "peanut should be avoided until the child is 3 years old", ["avoid", "3 years", "three years", "delayed", "not until"],
    "as early as 4 to 6 months of age", ["4 to 6 months", "4-6 months", "four to six months", "early introduction", "6 months", "4 months"],
    "Dietary recommendations for infants at risk of allergy", "2008-01-15",
    "For infants at high risk of allergy, it is advised that peanut-containing foods be avoided until the child reaches 3 years of age.",
    "Addendum guidelines for the prevention of peanut allergy in the United States", "2017-01-05",
    "Infants at high risk of peanut allergy should have peanut-containing foods introduced as early as 4 to 6 months of age, after evaluation. Early introduction reduces the risk of developing peanut allergy. This supersedes earlier advice to delay peanut until age 3.",
    undated_old=True)

rev("md-mpox", "medicine",
    "What is the WHO's preferred name for the disease previously called monkeypox?",
    "monkeypox", ["monkeypox"],
    "mpox", ["mpox"],
    "Monkeypox fact sheet", "2022-05-20",
    "Monkeypox is a viral zoonotic disease caused by the monkeypox virus. The disease is officially known as monkeypox.",
    "WHO recommends new name for monkeypox disease", "2022-11-28",
    "Following consultations, the WHO will use the new preferred term mpox as a synonym for monkeypox, and recommends that mpox be adopted as the name of the disease. This supersedes the earlier name.")

rev("md-mammogram", "medicine",
    "At what age does the US Preventive Services Task Force recommend women at average risk start biennial mammography screening?",
    "age 50", ["50", "fifty"],
    "age 40", ["40", "forty"],
    "USPSTF recommendation: breast cancer screening", "2016-01-12",
    "The Task Force recommends biennial screening mammography for women aged 50 to 74 years. The decision to start screening before age 50 should be an individual one.",
    "USPSTF final recommendation: breast cancer screening", "2024-04-30",
    "The Task Force now recommends biennial screening mammography for all women starting at age 40 and continuing through age 74. This supersedes the previous recommendation to start at 50.")

# --------------------------------------------------------------------------------------
# BUSINESS
# --------------------------------------------------------------------------------------
rev("bz-alphabet", "business",
    "What is the parent company of Google?",
    "Google Inc. is itself the parent company", ["google inc", "google itself", "no parent", "google is the parent", "is its own"],
    "Alphabet Inc.", ["alphabet"],
    "Google Inc. corporate structure", "2015-02-02",
    "Google Inc. is a publicly traded company and is the parent of all Google products and subsidiaries, including YouTube and Android. Google Inc. has no parent company.",
    "Alphabet becomes the parent company of Google", "2015-10-02",
    "Google has completed its reorganisation under a new holding company, Alphabet Inc. Google is now a wholly owned subsidiary of Alphabet. This supersedes the earlier structure.")

rev("bz-twitter-owner", "business",
    "Who owns the social media platform Twitter (X)?",
    "it is a publicly traded company owned by its shareholders", ["public", "shareholders", "publicly traded", "listed"],
    "Elon Musk, through X Corp", ["musk"],
    "Twitter, Inc. ownership", "2022-03-01",
    "Twitter, Inc. is a publicly traded company listed on the New York Stock Exchange and owned by its shareholders.",
    "Elon Musk completes acquisition of Twitter", "2022-10-27",
    "Elon Musk has completed his acquisition of Twitter, taking the company private. Twitter is now owned by Musk and has been merged into X Corp. This supersedes earlier ownership information.")

# --------------------------------------------------------------------------------------
# CONTROL ITEMS (stable facts, single document, no temporal conflict)
# --------------------------------------------------------------------------------------
ctl("c-light", "science", "What is the speed of light in vacuum?", "299,792,458 metres per second", ["299,792,458", "299792458", "3 x 10^8", "300,000 km"], "Physical constants", "2018-03-01", "The speed of light in vacuum is exactly 299,792,458 metres per second, a defined constant in the SI.")
ctl("c-canberra", "geography", "What is the capital city of Australia?", "Canberra", ["canberra"], "Australia country profile", "2019-05-14", "Canberra is the capital city of Australia. It is located in the Australian Capital Territory and is the seat of the federal government.")
ctl("c-python-creator", "software", "Who created the Python programming language?", "Guido van Rossum", ["guido", "van rossum"], "History of Python", "2017-09-04", "Python was created by Guido van Rossum and first released in 1991. Van Rossum led the language's development for many years as its Benevolent Dictator For Life.")
ctl("c-404", "software", "What does the HTTP status code 404 mean?", "Not Found", ["not found"], "HTTP status codes reference", "2020-01-20", "The HTTP 404 Not Found status code indicates that the server cannot find the requested resource.")
ctl("c-boiling", "science", "At what temperature does water boil at standard atmospheric pressure?", "100 degrees Celsius", ["100"], "Properties of water", "2016-02-11", "At standard atmospheric pressure, water boils at 100 degrees Celsius (212 degrees Fahrenheit).")
ctl("c-bones", "medicine", "How many bones are in the adult human body?", "206", ["206", "two hundred and six"], "Human skeletal system", "2019-08-30", "The adult human skeleton consists of 206 bones. Infants are born with around 270 bones, many of which fuse during growth.")
ctl("c-gold", "science", "What is the chemical symbol for gold?", "Au", ["au"], "Chemical elements: gold", "2015-11-09", "Gold is a chemical element with the symbol Au, from the Latin aurum, and atomic number 79.")
ctl("c-jupiter", "science", "What is the largest planet in the Solar System?", "Jupiter", ["jupiter"], "The planets of the Solar System", "2018-07-23", "Jupiter is the largest planet in the Solar System, with a mass more than twice that of all the other planets combined.")
ctl("c-nehru", "history", "Who wrote the book The Discovery of India?", "Jawaharlal Nehru", ["nehru"], "The Discovery of India", "2014-10-02", "The Discovery of India was written by Jawaharlal Nehru during his imprisonment at Ahmednagar Fort and was published in 1946.")
ctl("c-constitution", "law", "On what date did the Constitution of India come into force?", "26 January 1950", ["26 january 1950", "january 26, 1950", "1950"], "The Constitution of India", "2017-01-26", "The Constitution of India was adopted on 26 November 1949 and came into force on 26 January 1950, which is celebrated as Republic Day.")
ctl("c-git", "software", "Who created the Git version control system?", "Linus Torvalds", ["torvalds", "linus"], "A short history of Git", "2019-04-07", "Git was created by Linus Torvalds in 2005 for the development of the Linux kernel.")
ctl("c-sql", "software", "What does SQL stand for?", "Structured Query Language", ["structured query language"], "Introduction to SQL", "2016-06-15", "SQL stands for Structured Query Language and is the standard language for managing relational databases.")
ctl("c-rbi-founded", "history", "In which year was the Reserve Bank of India established?", "1935", ["1935"], "History of the Reserve Bank of India", "2015-04-01", "The Reserve Bank of India was established on 1 April 1935 in accordance with the Reserve Bank of India Act, 1934.")
ctl("c-taj", "geography", "In which city is the Taj Mahal located?", "Agra", ["agra"], "The Taj Mahal", "2018-02-14", "The Taj Mahal is a white marble mausoleum located in Agra, Uttar Pradesh, on the bank of the river Yamuna.")
ctl("c-pacific", "geography", "What is the largest ocean on Earth?", "the Pacific Ocean", ["pacific"], "The world's oceans", "2017-07-19", "The Pacific Ocean is the largest and deepest of Earth's oceans, covering about a third of the planet's surface.")
ctl("c-relativity", "science", "Who proposed the theory of general relativity?", "Albert Einstein", ["einstein"], "General relativity", "2015-11-25", "The theory of general relativity was published by Albert Einstein in 1915 and describes gravity as the curvature of spacetime.")
ctl("c-https-port", "software", "What is the default TCP port for HTTPS?", "443", ["443"], "Well-known network ports", "2019-10-10", "HTTPS uses TCP port 443 by default, while plain HTTP uses port 80.")
ctl("c-isro-hq", "science", "Where is the headquarters of ISRO located?", "Bengaluru", ["bengaluru", "bangalore"], "About ISRO", "2020-08-15", "The Indian Space Research Organisation is headquartered in Bengaluru, Karnataka.")
ctl("c-ganga", "geography", "What is the longest river in India?", "the Ganga (Ganges)", ["ganga", "ganges"], "Rivers of India", "2016-09-21", "The Ganga, also known as the Ganges, is the longest river in India, flowing about 2,525 kilometres from the Himalayas to the Bay of Bengal.")
ctl("c-dna", "science", "Who are credited with discovering the double-helix structure of DNA?", "James Watson and Francis Crick", ["watson", "crick"], "Structure of DNA", "2018-04-25", "The double-helix structure of DNA was described by James Watson and Francis Crick in 1953, building on X-ray diffraction data from Rosalind Franklin and Maurice Wilkins.")


# --------------------------------------------------------------------------------------
# Rendering documents with varied date formats
# --------------------------------------------------------------------------------------
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def _fmt(date, style):
    y, m, d = (int(x) for x in date.split("-"))
    mon = MONTHS[m - 1]
    suffix = "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return {
        0: f"Published: {d} {mon} {y}",
        1: f"Date: {date}",
        2: f"Last updated: {mon} {y}",                       # month precision only
        3: f"Press release dated {d:02d}/{m:02d}/{y}",
        4: f"Notification dated {d}{suffix} {mon}, {y}",
        5: f"(Issued {d} {mon[:3]} {y})",
        6: f"{mon} {d}, {y}",
    }[style]


def _fmt_effective(date, style):
    y, m, d = (int(x) for x in date.split("-"))
    mon = MONTHS[m - 1]
    return {
        0: f"Effective from: {d} {mon} {y}",
        1: f"With effect from {d:02d}-{m:02d}-{y}",
        2: f"w.e.f. {d:02d}.{m:02d}.{y}",
    }[style]


def _style(key, n):
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % n


def render_doc(doc_id, title, date, body, effective=None, undated=False):
    lines = [title]
    if not undated:
        lines.append(_fmt(date, _style(doc_id, 7)))
        if effective and effective != date:
            lines.append(_fmt_effective(effective, _style(doc_id + "e", 3)))
    lines.append("")
    lines.append(body)
    return "\n".join(lines)


def build():
    docs = []
    for it in R:
        o, n = it["old"], it["new"]
        docs.append(dict(doc_id=f"{it['id']}#old", item=it["id"], role="old", title=o["title"],
                         true_date=o["date"], true_effective=None, undated=it["undated_old"],
                         text=render_doc(f"{it['id']}#old", o["title"], o["date"], o["body"], None, it["undated_old"])))
        docs.append(dict(doc_id=f"{it['id']}#new", item=it["id"], role="new", title=n["title"],
                         true_date=n["date"], true_effective=n.get("effective"), undated=False,
                         text=render_doc(f"{it['id']}#new", n["title"], n["date"], n["body"], n.get("effective"), False)))
    for it in C:
        docs.append(dict(doc_id=f"{it['id']}#ctl", item=it["id"], role="control", title=it["title"],
                         true_date=it["date"], true_effective=None, undated=False,
                         text=render_doc(f"{it['id']}#ctl", it["title"], it["date"], it["body"], None, False)))
    out = dict(reversals=R, controls=C, documents=docs)
    path = pathlib.Path(__file__).with_name("temprev.json")
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    ids = [it["id"] for it in R] + [it["id"] for it in C]
    assert len(ids) == len(set(ids)), "duplicate ids"
    for it in R:
        assert it["old"]["date"] < it["change_date"] <= "2026-01-01", it["id"]
        assert it["new"]["date"] <= "2026-01-01", it["id"]
    print(f"reversals={len(R)} controls={len(C)} documents={len(docs)} "
          f"undated_old={sum(it['undated_old'] for it in R)} -> {path}")
    from collections import Counter
    print("domains:", dict(Counter(it["domain"] for it in R)))


if __name__ == "__main__":
    build()
