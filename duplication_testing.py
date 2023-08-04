from thefuzz import fuzz
from thefuzz import process
import requests
import json


#Setting up API - will change to env variable in prod
apiKey = "kXvU9CuUw859_0lh7De49UdkNup"

headers = {
    "accept": "application/json",
    "x-api-key": "kXvU9CuUw859_0lh7De49UdkNup"
}



collection_dictionary = {
    '0N1 Force': '0x3bf2922f4520a8ba0c2efc3d2a1539678dad5e9d',
    '1989 Sisters': '0x657fabdb226abc59227e02e94089afbc67a597fe',
    '3Landers': '0xb4d06d46a8285f4ec79fd294f78a881799d8ced9',
    'Mooncats': '0xc3f733ca98e0dad0386979eb96fb1722a1a05e69',
    'adidas for Prada re-source': '0x7dec38e3874ecbc842cc61e66c1386aca0c0ea1f',
    'Ape Kids Club (AKC)': '0x9bf252f97891b907f002f2887eff9246e3054080',
    'Akuma Origins': '0xfa7e3f898c80e31a3aedeae8b0c713a3f9666264',
    'Akutars': '0xaad35c2dadbe77f97301617d82e661776c891fa9',
    'alien frens': '0x123b30e25973fecd8354dd5f41cc45a3065ef88c',
    'Chromie Squiggle': '0x059edd72cd353df5106d2b9cc5ab83a52287ac3a',
    'Genesis': '0x059edd72cd353df5106d2b9cc5ab83a52287ac3a',
    'NimBuds': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'CENTURY': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Petro National': '0x64780ce53f6e966e18a22af13a2f97369580ec11',
    'Floating World Genesis': '0x64780ce53f6e966e18a22af13a2f97369580ec11',
    'QWERTY': '0x64780ce53f6e966e18a22af13a2f97369580ec11',
    'Contractions': '0x64780ce53f6e966e18a22af13a2f97369580ec11',
    'New Worlds': '0x64780ce53f6e966e18a22af13a2f97369580ec11',
    'Enchiridion': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'I Saw It in a Dream': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Octo Garden': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Eccentrics': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Gizmobotz': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Radiance': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Low Tide': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Divisions': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Speckled Summits': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'HyperHash': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Lava Glow': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '70s Pop Ghost Bonus Pack 👻': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Alien Clock': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'celestial cyclones': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'glitch crystal monsters': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Dot Grid': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Flowers': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Transitions': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'LeWitt Generator Generator': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ecumenopolis': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Unigrids': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Endless Nameless': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Rinascita': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Cells': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Nucleus': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'The Liths of Sisyphus': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Calendart': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Timepiece': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Labyrometry': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Pigments': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ringers': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Obicera': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Scribbled Boundaries': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Tangled': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Organized Disruption': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Wave Schematics': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Brushpops': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'SpiroFlakes': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Alien Insects': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Geometry Runners': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Eccentrics 2: Orbits': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Cyber Cities': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Good Vibrations': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Rapture': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Unknown Signals': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'phase': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'autoRAD': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Beatboxes': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Neighborhood': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Trossets': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Dot Matrix Gradient Study': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Utopia': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'PrimiLife': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'High Tide': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Fake Internet Money': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'We': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Warp': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Moments': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'UltraWave 369': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'a heart and a soul': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Fragments of an Infinite Field': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Color Study': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Seadragons': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'spawn': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Democracity': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Meridian': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Phototaxis': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Gravity 16': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ouroboros': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Blaschke Ballet': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Bloom': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Augmented Sequence': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Spectron': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Chroma Theory': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Himinn': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Rituals - Venice': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Skulptuur': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Letters to My Future Self': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'mono no aware': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Space Birds': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Beauty in the Hurting': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    8: '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Gen 2': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'mecha suits': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'FOCUS': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Amoeba': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Quarantine': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Swing': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'little boxes on the hillsides, child': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'THE SOURCE CoDE': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Blockbob Rorschach': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'CryptoNewYorker': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'R3sonance': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Mental pathways': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '444(4)': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Recursion': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Murano Fantasy': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Rotae': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Paramecircle': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Aithérios': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Parade': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Coquina': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Prismatic': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Construction Token': '0x059edd72cd353df5106d2b9cc5ab83a52287ac3a',
    'Sentience': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Saturazione': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Friendship Bracelets': '0x942bc2d3e7a589fe5bd4a5c6ef9727dfd82f5c8a',
    'Marfa Yucca': '0x942bc2d3e7a589fe5bd4a5c6ef9727dfd82f5c8a',
    '24 Heures': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Beauty of Skateboarding': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Scoundrels': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Edifice': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Placement': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Asemica': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Through the Window': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Reflection': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Autology': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '27-Bit Digital': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Nebula': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Freehand': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Dive': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Loom': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Bent': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Gazers': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Electriz': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Paths': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Squares and Triangles': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Time Atlas 🌐': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'The Eternal Pump': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'geVIENNAratives': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Spiromorphs': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Pieces of Me': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Dream Engine': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Tropism': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Vortex': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Getijde': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Kai-Gen': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Incomplete Control': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Attraction': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Archetype': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Glow': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Cushions': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Jiometory No Compute - ジオメトリ ハ ケイサンサレマセン': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Chimera': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'The Wrapture': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Maps for grief': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Summoning Ritual': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Time Squared': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'AlphaModica': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Synesthesia': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Pixel Glass': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Pizza 1o1': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Maps': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Two Mathematicians': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'InC': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Freeplan': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Stations': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Heavenly Bodies': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'HashCrash': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Facets': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Pathfinders': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Cosmic Reef': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Undercover': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Roamings': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Legends of Metaterra': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Fernweh': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Screens': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Spotlight': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Machine Comics': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Cosmodesias': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Masonry': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'EnergySculpture': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Non Either': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Para Bellum ': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Haywire Café ': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Click': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Thereidoscope': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Tentura': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Exhibition: 3291': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'entretiempos': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'PrimiEnd': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Lacunae': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '720 Minutes': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Foliage': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Time travel in a subconscious mind': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'pseudomods': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Silhouette': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Isodream': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Quantum Collapses': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Strata': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Perpetua': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Liquid Ruminations': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Neophyte MMXXII': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Apparitions': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Window': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Automatism': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Memories of Qilin': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'OnChainChain': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ancient Courses of Fictional Rivers': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Supermental': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Mazinaw': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'AlgoBeats': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Inspirals': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Corners': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Túnel Dimensional': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Flux': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Mind Maze': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Cryptoblots': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Hieroglyphs': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Assemblage': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Hōrō by makio135': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Primordial': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Imperfections': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Anticyclone': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Zupermat': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ode to Penrose by uMathA': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Cattleya by Ben Snell': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Colorspace by Tabor Robak': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Galaxiss': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '100 PRINT': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Faceless': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Daisies by Natthakit Susanthitanon (NSmag)': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    "Photon's Dream by Harvey Rayner": '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Divenire by Emanuele Pasin': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Rotor by Sebastián Brocher (CryptoArte)': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Maps of Nothing by Steve Pikelny': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'the spring begins with the first rainstorm by Cole Sternberg': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Collapsed Sequence by toiminto': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Assorted Positivity by steganon': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Light Beams': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'montreal friend scale by amon tobin': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Fermented Fruit by cyberia': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'GHOST IN THE CODE by Kazuhiro Tanimoto': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Woah La Coaster by Blockwares': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Total Strangers by Artem Verkhovskiy x Andy Shaw': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '3:19': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Sudfah': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Latent Spirits': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Empyrean': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Metropixeland': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Steps': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Alan Ki Aankhen': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Running Moon': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Scribblines': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Polychrome Music': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'FAKE IT TILL YOU MAKE IT': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'undead wyverns': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ieva': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ensō': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Vahria': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'RASTER': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Being Yourself While Fitting In': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Balletic': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Glass': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '80s Pop Variety Pack - for experts only 🕹': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Avalon': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Totem of Taste': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Aerial View': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Departed': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Staccato': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'The Inner World': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Pointila': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Interferences': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Thoughts of Meadow': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Essenza': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'D-D-Dots': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Arcadia': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ode to Untitled': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Gazettes': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'flora, fauna, false gods & floods': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Erratic': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Act of Emotion': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Stains on a Canvas': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Sandaliya': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Fontana': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Primitives': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'CENTURY 2052': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Paper Armada': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Rectangles (for Herbert)': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'JPEG': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Intersections': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Wabi Sabi': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Tide Predictor': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Ingress': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Fleur': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'ORI': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    '♫ ByteBeats': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Seedlings': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Structures': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Metaphysics': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Pre-Process': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'VOXΞL': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Dipolar': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Ego Death': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Pointers': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Your Story': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Miragem': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Synapses': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Imposter Syndrome': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Hyper Drive: A-Side': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Race Condition': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Volute': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Implications': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Good, Computer': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Through Curved Air': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Libra': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'The Field': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Dynamic Slices': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Algobots': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Such A Lovely Time': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Aragnation': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Ad Extremum Terrae': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'The Harvest': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'NimTeens': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Tout tracé': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
    'Elementals': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Void': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Origami Dream': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'CryptoGodKing': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Gravity Grid': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '70s Pop Series One': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Asterisms': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Gen 3': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Dear Hash,': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Variant Plan': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'The Opera': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Stipple Sunsets': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Star Flower': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Subscapes': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'P:X': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Talking Blocks': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Aurora IV': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Rhythm': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Color Magic Planets': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Watercolor Dreams': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'View Card': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Event Horizon Sunset (Series C)': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '70s Pop Super Fun Summertime Bonus Pack 🍸': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Bubble Blobby': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ode to Roy': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'AlgoRhythms': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Traversals': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Patchwork Saguaros': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Petri': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Messengers': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Abstraction': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Elevated Deconstructions': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Antennas': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Andradite': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Frammenti': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'CatBlocks': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'The Blocks of Art': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Breathe You': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'dino pals': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Return': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Fidenza': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    "Space Debris [m'aider]": '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Singularity': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Space Debris [warning]': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Space Debris [ravaged]': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Incantation': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Panelscape 🅰🅱': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'PrimiDance': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '70s Pop Series Two': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Stroming': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Patterns of Life': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Orthogone': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Dreams': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Ignition': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Hashtractors': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'planets': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Libertad Parametrizada': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Sigils': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Portal': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'CryptoVenetian': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Gravity 12': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    '[Dis]entanglement': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'sail-o-bots': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Spaghettification': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'Autoglyphs': '0xd4e4078ca3495de5b1d4db434bebc5a986197782',
    'Avid Lines': '0xdfacd840f462c27b0127fc76b63e7925bed0f9d5',
    'Azuki': '0xed5af388653567af2f388e6224dc7c4b3241c544',
    'Azuki Elemental Beans': '0x3af2a97414d1101e2107a70e7f33955da1346305',
    '(B)APETAVERSE': '0x4addca4c07a5e9a6b4973094d03ad5aae7735e5b',
    'BEANZ Official': '0x306b1ea3ecdf94ab739f1910bbda052ed4a9f949',
    'BitcoinBillionaires': '0x80d77b4ae7cd0d7a21fd3c1b2da25a4a06b63923',
    'BMC Blockchain Miners Club': '0x47bd71b482b27ebdb57af6e372cab46c7280bf44',
    'Blvck Genesis': '0x83b070e842adba2397113c4bca70c00d7df00729',
    'Deez Nuts (Official Nuts)': '0xb1469271ff094d7fb2710b0a69a80a01ec5dbf24',
    'Boki': '0x248139afb8d3a2e16154fbe4fb528a3a214fd8e7',
    'Bonsai by ZENFT': '0xec9c519d49856fd2f8133a0741b4dbe002ce211b',
    'Bored Ape Kennel Club': '0xba30e5f9bb24caa003e9f2f0497ad287fdf95623',
    'Bored Ape Yacht Club': '0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
    'Bored Mummy Waking Up': '0xf621b26ce64ed28f42231bcb578a8089f7958372',
    'Bricktopians by Law Degree': '0x9eeeaf684e228c2d5c89435e010acc02c41dc86b',
    'BullsOnTheBlock': '0x3a8778a58993ba4b941f85684d74750043a4bb5f',
    'BRAiN VOMiTS GARDEN': '0x33e1977d6593050520b1fe2d5c586376ad07046d',
    'Caked Apes Official': '0xc1922a5abfa18110827c0666b7bbac0389ab7396',
    'CATBOTICA': '0x25e5e2b4b8f11c32cdd48c2fb394fbda9a2861f7',
    'Champions Ascension': '0x13d15d8b7b2bf48cbaf144c5c50e67b6b635b5cd',
    'Chibi Apes': '0xc49a9ab342b6ea66792d4110e9ca0ab36e3a5674',
    'Chiptos': '0xf3ae416615a4b7c0920ca32c2dfebf73d9d61514',
    'Chubbiverse Frens': '0x42f1654b8eeb80c96471451b1106b63d0b1a9fe1',
    'Coalition Crew 2.0': '0xcefc0a83564dd2a083b83b4a73bbae97e40fa7ea',
    'Cool Cats NFT': '0x1a92f7381b9f03921564a437210bb9396471050c',
    "Coolman's Universe": '0xa5c0bd78d1667c13bfb403e2a3336871396713c5',
    'COVIDPunks!': '0xe4cfae3aa41115cb94cff39bb5dbae8bd0ea9d41',
    'Crash Test Joyride': '0x3bf42951001bb7cb3cc303068fe87debf696ee3d',
    'Creature World': '0xc92ceddfb8dd984a89fb494c376f9a48b999aafc',
    'CROAKZ by McGill!': '0x7cae7b9b9a235d1d94102598e1f23310a0618914',
    'Crookz by NIXON': '0x7da30048214e112dbc41a645e37f9640ac62799e',
    'CrypToadz by GREMPLIN': '0x1cb1a5e65610aeff2551a50f76a87a7d3fb649c6',
    'CryptoBeasts': '0xa74e199990ff572a320508547ab7f44ea51e6f28',
    'Crypto Bull Society': '0x469823c7b84264d1bafbcd6010e9cdf1cac305a3',
    'Crypto Champions Collection': '0x97a923ed35351a1382e6bcbb5239fc8d93360085',
    'Crypto Coven': '0x5180db8f5c931aae63c74266b211f580155ecac8',
    'CryptoDickbutts': '0x42069abfe407c60cf4ae4112bedead391dba1cdb',
    'Crypto Hobos': '0xd153f0014db6d1f339c6340d2c9f59214355d9d7',
    'CryptoHoots Steampunk Parliament': '0x5754f44bc96f9f0fe1a568253452a3f40f5e9f59',
    'CryptoPunks': '0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb',
    'CyberBabies.io': '0x991a546a167ceb2a6a7c344c9d85269ac03035d9',
    'CyberKongz Baby/Incubator': '0x57a204aa1042f6e66dd7730813f4024114d74f37',
    'CyberKongz Genesis': '0x57a204aa1042f6e66dd7730813f4024114d74f37',
    'Dapper Dinos NFT': '0x2d0ee46b804f415be4dc8aa1040834f5125ebd2e',
    'DeadHeads': '0x6fc355d4e0ee44b292e50878f49798ff755a5bbc',
    'Decentraland': '0xf87e31492faf9a91b02ee0deaad50d51d56d5d4d',
    'DEGEN TOONZ COLLECTION': '0x19b86299c21505cdf59ce63740b240a9c822b5e4',
    'DeGods': '0x8821bee2ba0df28761afff119d66390d594cd280',
    'DentedFeelsNFT': '0xc5e55e4bd5fef12831b5a666fc9e391538acdc45',
    'Desperate ApeWives': '0xf1268733c6fb05ef6be9cf23d24436dcd6e0b35e',
    'DEZUKI': '0xad4d85257c815a4b2c7088a664e958b035b24323',
    'Doodles': '0x8a90cab2b38dba80c64b7734e58ee1db38b8992e',
    'dotdotdots': '0xce25e60a89f200b1fa40f6c313047ffe386992c3',
    'DourDarcels': '0x8d609bd201beaea7dccbfbd9c22851e23da68691',
    "Dr. ETHvil's 3D FrankenPunks": '0x1fec856e25f757fed06eb90548b0224e91095738',
    'Dysto Apez Official': '0x648e8428e0104ec7d08667866a3568a72fe3898f',
    'DystoPunks': '0xbea8123277142de42571f1fac045225a1d347977',
    'EightBit Me': '0x6080b6d2c02e9a0853495b87ce6a65e353b74744',
    'HENI: Damien Hirst - The Empresses': '0x3bf99d504e67a977f88b417ab68d34915f3a1209',
    'Encryptas': '0x6391a41819c699972b75bf61db6b34ef940c96f0',
    'The Evolving Forest Genesis': '0xd49eccf40689095ad9e8334d8407f037e2cf5e42',
    'FameLadySquad': '0xf3e6dbbe461c6fa492cea7cb1f5c5ea660eb1b47',
    'Fang Gang': '0x9d418c2cae665d877f909a725402ebd3a0742844',
    'Fast Food Frens Collection': '0x4721d66937b16274fac603509e9d61c5372ff220',
    'Fat Ape Club': '0xf3114dd5c5b50a573e66596563d15a630ed359b4',
    'Feline Fiendz NFT': '0xacfa101ece167f1894150e090d9471aee2dd3041',
    'FishyFam': '0x63fa29fec10c997851ccd2466dad20e51b17c8af',
    'FLUF World': '0xccc441ac31f02cd96c153db6fd5fe0a2f4e6a68d',
    'Forgotten Runes Wizards Cult': '0x521f9c7505005cfa19a8e5786a9c3c9c9f5e6f42',
    'FoxyFam': '0x444467738cf0c5bcca9c1d6f66670f4c493e53ff',
    'frankfrank': '0x91680cf5f9071cafae21b90ebf2c9cc9e480fb93',
    'fRiENDSiES': '0xe5af63234f93afd72a8b9114803e33f6d9766956',
    'Fudders': '0xba60f470f16654ec79f0d1b2f1c0c12390107a56',
    'FVCK_CRYSTAL//': '0x7afeda4c714e1c0a2a1248332c100924506ac8e6',
    'Fyat Lux (Dawn Collection)': '0x14c4471a7f6dcac4f03a81ded6253eaceff15b3d',
    'GalacticApes': '0x12d2d1bed91c24f878f37e66bd829ce7197e4d14',
    'Galaktic Gang': '0xf4cd7e65348deb24e30dedee639c4936ae38b763',
    'Galaxy-Eggs': '0xa08126f5e1ed91a635987071e6ff5eb2aeb67c48',
    'Generative Dungeon': '0x18487d2cac946c7fe800855c4039aac210f68baa',
    'Girlies NFT': '0x4f7e2a72a99d45f4fd5a2fc211f8dc5c36a049bd',
    'Goons of Balatroon': '0x8442dd3e5529063b43c69212d64d5ad67b726ea6',
    'GossApe Girl': '0x3bf447963c8d8bdf06751528de40efb0849f3037',
    'Gutter Cat Gang': '0xedb61f74b0d09b2558f1eeb79b247c1f363ae452',
    'Gutter Juice': '0x092bbc993042a69811d23feb0e64e3bfa0920c6a',
    'Habbo Avatars': '0x8a1bbef259b00ced668a8c69e50d92619c672176',
    'Hall Of Fame Goat Lodge': '0x004f5683e183908d0f6b688239e3e2d5bbb066ca',
    'HAPE PRIME': '0x4db1f25d3d98600140dfc18deb7515be5bd293af',
    'Hashmasks': '0xc2c747e0f7004f9e8817db2ca4997657a7746928',
    'HIDDEN IN NOISE': '0xf55dd62034b534e71cb17ef6e2bb112e93d6131a',
    'Cypher by Hideki Tsukamoto': '0xdda32aabbbb6c44efc567bac5f7c35f185338456',
    'HUXLEY Robots': '0xbeb1d3357cd525947b16a9f7a2b3d50b50b977bd',
    'HV-MTL': '0x4b15a9c28034dc83db40cd810001427d3bd7163d',
    'HYPEBEARSCLUB.OFFICIAL': '0x14e0a1f310e2b7e321c91f58847e98b8c802f6ef',
    'IlluminatiNFT': '0x26badf693f2b103b021c670c852262b379bbbe8a',
    'Impostors Genesis Aliens': '0x3110ef5f612208724ca51f5761a69081809f03b7',
    'Imps by SuperNfty': '0x3cd859effbb3375acde3e2941c7e8e833221dfb1',
    'inBetweeners by GianPiero': '0x94638cbf3c54c1f956a5f05cbc0f9afb6822020d',
    'Infinites AI': '0xa7f767865fce8236f71adda56c60cf2e91dadc00',
    'Invisible Friends': '0x59468516a8259058bad1ca5f8f4bff190d30e066',
    'IO: Imaginary Ones': '0x716f29b8972d551294d9e02b3eb0fc1107fbf4aa',
    'Jadu Hoverboard': '0xeda3b617646b5fc8c9c696e0356390128ce900f8',
    'Jadu Jetpack': '0xd0f0c40fcd1598721567f140ebf8af436e7b97cf',
    'JUNGLE FREAKS GENESIS': '0x7e6bc952d4b4bd814853301bee48e99891424de0',
    'Knights of Degen': '0xe3f92992bb4f0f0d173623a52b2922d65172601d',
    'Koala Intelligence Agency': '0x3f5fb35468e9834a43dca1c160c69eaae78b6360',
    'Kohi Kintsugi': '0xdf6e32d85d17e907e0da157fab7c12788e7161da',
    'Lil Baby Ape Club': '0x918f677b3ab4b9290ca96a95430fd228b2d84817',
    'Little Lemon Friends': '0x0b22fe0a2995c5389ac093400e52471dca8bb48a',
    'Lonely Alien Space Club': '0x343f999eaacdfa1f201fb8e43ebb35c99d9ae0c1',
    'Long Neckie Ladies': '0xbb3d13260b3f6893ace34a4284be70eccf4cc0f1',
    'Loot (for Adventurers)': '0xff9c1b15b16263c61d017ee9f65c50e4ae0113d7',
    'Mad Rabbits Riot Club': '0x57fbb364041d860995ed610579d70727ac51e470',
    'Moon Ape Lab Genesis': '0x34c4eba1966b502dfcf0868b6f271d85cc8a2312',
    'Mars Cats Voyage': '0xdd467a6c8ae2b39825a452e06b4fa82f73d4253d',
    'Meebits': '0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7',
    'MekaVerse': '0x9a534628b4062e123ce7ee2222ec20b86e16ca8f',
    'Mems, Voyage One': '0x745fc083f4336a4151c76de9f598e0f67991c3fa',
    'Meta Eagle Club - THE COLLECTION': '0xeb6dffb87315a2bdf4dedf72b993adc960773a0d',
    'Metasaurs by Dr. DMT': '0xf7143ba42d40eaeb49b88dac0067e54af042e963',
    'MEV Army': '0x99cd66b3d67cd65fbafbd2fd49915002d4a2e0f2',
    'mfers': '0x79fcdef22feed20eddacbb2587640e45491b757f',
    'MidnightBreeze': '0xd9c036e9eef725e5aca4a22239a23feb47c3f05d',
    'Milady Maker': '0x5af0d9827e0c53e4799bb226655a1de152a425a5',
    'Mind the Gap by MountVitruvius': '0x0e42ffbac75bcc30cd0015f8aaa608539ba35fbb',
    'Mines of Dalarnia Mining Apes Collection': '0x8e74ec33406fca20c1be7b2a6c4135fc7cfac9e8',
    'MoodRollers by Lucas Zanotto': '0xe3234e57ac38890a9136247eadfe1860316ff6ab',
    'More Than Gamers | MTG': '0x49907029e80de1cbb3a46fd44247bf8ba8b5f12f',
    'MUSHROHMS': '0x133ba8f869f3ae35a5ca840ba20acfa31b0e2a61',
    'Mutant Ape Yacht Club': '0x60e4d786628fea6478f785a6d7e704777c86a7c6',
    'MutantCats': '0xaadba140ae5e4c8a9ef0cc86ea3124b446e3e46a',
    'My Fucking Pickle': '0xf78296dfcf01a2612c2c847f68ad925801eeed80',
    'Nakamigos': '0xd774557b647330c91bf44cfeab205095f7e6c367',
    'Never Fear Truth  by Johnny Depp': '0x06b3fcc9e79d724a08012f0b9f71bd03b415d334',
    'Ninja Squad Official': '0x8c186802b1992f7650ac865d4ca94d55ff3c0d17',
    'notBanksyEchoes': '0x925f7eb0fe634702049a1344119d4046965b5c8c',
    'Notorious Alien Space Agents': '0x7a1f56f9641d7bd8c57f0909959c894c97e39beb',
    'NounPunks.eth': '0xe169c2ed585e62b1d32615bf2591093a629549b6',
    'OctoHedz': '0x6e5a65b5f9dd7b1b08ff212e210dcd642de0db8b',
    'Official Dormant Dragons': '0xdb3b2e1f699caf230ee75bfbe7d97d70f81bc945',
    'The Official Surreals': '0xa406489360a47af2c74fc1004316a64e469646a5',
    'OG:Crystals': '0x368ad4a7a7f49b8fa8f34476be0fc4d04ce622f5',
    'Omnimorphs': '0xb5f3dee204ca76e913bb3129ba0312b9f0f31d82',
    'OnChainMonkey': '0x960b7a6bcd451c9968473f7bbfd9be826efd549a',
    'Opepen Edition': '0x6339e5e072086621540d0362c4e3cea0d643e114',
    'Otherdeed for Otherside': '0x34d85c9cdeb23fa97cb08333b511ac86e1c4e258',
    'Paradise Trippies': '0x4ca4d3b5b01207ffce9bea2db9857d4804aa89f3',
    'PEACEFUL GROUPIES': '0x4f89cd0cae1e54d98db6a80150a824a533502eea',
    'PeopleInThePlaceTheyLove': '0x496a2d17a89cbc4248e9b52c8003a50c648fbca0',
    'PhantaBear': '0x67d9417c9c3c250f61a83c7e8658dac487b56b09',
    'PixelMap': '0x050dc61dfb867e0fe3cf2948362b6c0f3faf790b',
    'Farm Land by Pixels': '0x5c1a0cc6dadf4d0fb31425461df35ba80fcbc110',
    'Private Jet Pyjama Party': '0x3598fff0f78dd8b497e12a3ad91febcfc8f49d9e',
    'Pop Art Cats by Matt Chessco': '0x1554f51f18f8e3fbe83e4442420e40efc57ff446',
    'Prime Ape Planet PAP': '0x6632a9d63e142f17a668064d41a21193b49b41a0',
    'Project NANOPASS': '0xf54cc94f1f2f5de012b6aa51f1e7ebdc43ef5afc',
    'Moonbirds': '0x23581767a106ae21c074b2276d25e5c3e136a68b',
    'Psychedelics Anonymous Component 2': '0xa7b6cb932eecacd956454317d59c49aa317e3c57',
    'Psychedelics Anonymous Printing Press': '0xc8e1de8dc39a758c7a50f659b53f787e0f1398bd',
    'Pudgy Penguins': '0xbd3531da5cf5857e7cfaa92426877b022e612cf8',
    'Purrnelopes Country Club': '0x9759226b2f8ddeff81583e244ef3bd13aaa7e4a1',
    'Quirkies Originals': '0x3903d4ffaaa700b62578a66e7a67ba4cb67787f9',
    'Rebel Bots': '0xbbe23e96c48030dc5d4906e73c4876c254100d33',
    'Regulars': '0x6d0de90cdc47047982238fcf69944555d27ecb25',
    'Robotos': '0x099689220846644f87d1137665cded7bf3422747',
    'Royal Society of Players': '0xb159f1a0920a7f1d336397a52d92da94b1279838',
    'Stoner Ape Club | SAC': '0x984f7b398d577c0adde08293a53ae9d3b6b7a5c5',
    'Sacred Skulls (Official)': '0xcf514faa49cb3133275eb4c9420e4161970ee806',
    'Sad Girls Bar': '0x335eeef8e93a7a757d9e7912044d9cd264e2b2d8',
    'SamuraiCats by Hiro Ando': '0xc8d2bf842b9f0b601043fb4fd5f23d22b9483911',
    'Sappy Seals': '0x364c828ee171616a39897688a831c2499ad972ec',
    'Satoshibles': '0x0b0b186841c55d8a09d53db48dc8cab9dbf4dbd6',
    'Secret Society of Whales': '0x88091012eedf8dba59d08e27ed7b22008f5d6fe5',
    'Sewer Pass': '0x764aeebcf425d56800ef2c84f2578689415a2daa',
    'Shonen Junk Official': '0xf4121a2880c225f90dc3b3466226908c9cb2b085',
    'Sipherian Flash': '0x09e0df4ae51111ca27d6b85708cfb3f1f7cae982',
    'Sipherian Surge': '0x9c57d0278199c931cf149cc769f37bb7847091e7',
    'Skeletongues': '0xb01db56d3cd07286af1d02f712afd7cdb6c7bc5c',
    'SmallBrosNFT': '0xb18380485f7ba9c23deb729bedd3a3499dbd4449',
    'SMOWL': '0x03b8d129a8f6dc62a797b59aa5eebb11ad63dada',
    'Sneaky Vampire Syndicate': '0x219b8ab790decc32444a6600971c7c3718252539',
    'The Doggies (Snoop Dogg)': '0xc7df86762ba83f2a6197e1ff9bb40ae0f696b9e6',
    'Society of Degenerate Apes (SODA)': '0xb184b9414e7d7c436b7097ed2c774bb56fae392f',
    'Solvency by Ezra Miller': '0x82262bfba3e25816b4c720f1070a71c7c16a8fc4',
    'SpacePunksClub': '0x45db714f24f5a313569c41683047f1d49e78ba07',
    'Squishy Squad NFT': '0x792496a3f678187e59e1d1d5e075799cd1e124c2',
    'Stoner Cats': '0xd4d871419714b778ebec2e22c7c53572b573706e',
    'SupDucks': '0x3fe1a4c1481c8351e91b64d5c398b159de07cbc5',
    'SuperCreators by IAC': '0x9c8d2f53f6bff84458f1c84fdaa1e4852ca958e3',
    'The Superlative Secret Society': '0xa7ee407497b2aeb43580cabe2b04026b5419d1dc',
    'SUPERPLASTIC: SUPERGUCCI': '0x78d61c684a992b0289bbfe58aaa2659f667907f8',
    'Super Yeti': '0x3f0785095a660fee131eebcd5aa243e529c21786',
    'Swampverse': '0x95784f7b5c8849b0104eaf5d13d6341d8cc40750',
    'Tasty Bones XYZ': '0x1b79c7832ed9358e024f9e46e9c8b6f56633691b',
    'The Alien Secret Society': '0x62d8ae32b0e6964d2126716cf3da70c2bd062d94',
    'The Art of Seasons': '0x5bd815fd6c096bab38b4c6553cfce3585194dff9',
    'Claylings': '0x8630cdeaa26d042f0f9242ca30229b425e7f243f',
    'Crypto.Chicks': '0x1981cc36b59cffdd24b01cc5d698daa75e367e04',
    'Damien Hirst - The Currency': '0xaadc2d4261199ce24a4b0a57370c4fcf43bb60aa',
    'The Doge Pound': '0xf4ee95274741437636e748ddac70818b4ed7d043',
    'The Humanoids': '0x3a5051566b2241285be871f650c445a88a970edd',
    'The Long Lost': '0x1347a97789cd3aa0b11433e8117f55ab640a0451',
    'The Loomi Heads': '0x0e5b1348bddc08b24efb3cca4f2a519da305cd4f',
    'The Lost Glitches': '0x8460bb8eb1251a923a31486af9567e500fc2f43f',
    'The Picaroons': '0x545f0a45ba06c7c5b1a5fb0b29008462ceea07b7',
    'The Plague NFT': '0x8c3fb10693b228e8b976ff33ce88f97ce2ea9563',
    'The Sad Cats': '0xb2a965b54be0b280c59f0503dd0aa2dbfa8ffff2',
    'The Space Bulls TSB': '0x07a8ba3f4fd4db7f3381c07ee5a309c1aace9c59',
    'The Squishiverse NFT': '0x67421c8622f8e38fe9868b4636b8dc855347d570',
    'the sunnies collection': '0x06fd3999fa72163c6f21f649587e6b6d670cdc8b',
    '- TronWars -': '0x537b2279d8f625a1b74cf3c1f0e2122fb047a6b0',
    'TheWhitelist.io - Aces': '0xb3b814ccd178de120687a9ad01c6886c56399198',
    'The Wicked Craniums': '0x85f740958906b317de6ed79663012859067e745b',
    'TOKYO PUNKS by SABET': '0x59a498d8cb5f0028591c865c44f55e30b76c9611',
    'TOPIA Worlds': '0x8d9710f0e193d3f95c0723eaaf1a81030dc9116d',
    'Toxic Skulls Club': '0x282a7d13152b3f51a3e31d46a2ca563f8554d85d',
    'Trippy Toadz NFT': '0x19cb5b009bdad0dad0404dd860b0bea75465e678',
    'tubby cats by tubby collective': '0xca7ca7bcc765f77339be2d648ba53ce9c8a262bd',
    'Unemployables': '0xe0be388ab81c47b0f098d2030a1c9ef190691a8a',
    'uwucrew': '0xf75140376d246d8b1e5b8a48e3f00772468b3c0c',
    'VaynerSports Pass VSP': '0xbce6d2aa86934af4317ab8615f89e3f9430914cb',
    'VeeFriends': '0xa3aee8bce55beea1951ef834b99f3ac60d1abeeb',
    'VOID - Visitors of Imma Degen': '0xdb55584e5104505a6b38776ee4dcba7dd6bb25fe',
    'The Vogu Collective': '0x18c7766a10df15df8c971f6e8c1d2bba7c7a410b',
    'Voxies': '0xfbe3ab0cbfbd17d06bdd73aa3f55aaf038720f59',
    'Wall St Bulls': '0x79da5fa272e8fb280cee4d0649aa6a9e4e62ceb0',
    'Weird Whales': '0x96ed81c7f4406eff359e27bff6325dc3c9e042bd',
    'Whiskers': '0x0ff55bd2efbef8356298fa2be134919b2b529362',
    'Wicked Ape Bone Club': '0xbe6e3669464e7db1e1528212f0bff5039461cb82',
    'Women and Weapons': '0x338866f8ba75bb9d7a00502e11b099a2636c2c18',
    'World of Women': '0xe785e82358879f061bc3dcac6f0444462d4b5330',
    'WVRPS by WarpSound (Official)': '0xcbc67ea382f8a006d46eeeb7255876beb7d7f14d',
    'X Rabbits Club': '0x534d37c630b7e4d2a6c1e064f3a2632739e9ee04',
    'Yeti Town NFT': '0x65c5493e6d4d7bf2da414571eb87ed547eb0abed',
    'Zunkz': '0x031920cc2d9f5c10b444fd44009cd64f829e7be2'
}


#This function is used in order to match the closest possible collection address. This allows for shorthand names and common misspellings.
def getCollection (query):

    bestMatch = process.extractOne(query, collection_dictionary.keys())

    #this allows for some mistakes to be made when typing collection name but cuts it off when its likely to return the wrong one
    if bestMatch[1] < 75:
        return "No collection found. Check for spelling mistakes."
    
    collectionName = bestMatch[0]
    print("Found collection: " + collectionName)
    address = collection_dictionary[bestMatch[0]]

    return address

def getFloor(collectionAddress):
    url = "https://api.ebitlabs.com/v1/series_floor?contract_address_or_opensea_slug="+collectionAddress

    floorPrice = requests.get(url, headers=headers)
    floorPrice = json.loads(floorPrice.text)
    floorPrice = str(floorPrice['floor']) + " ETH"

    print(floorPrice)
    return floorPrice


def  getMarketCap(collectionAddress):
    url = "https://api.ebitlabs.com/v1/series_market_cap?contract_address_or_opensea_slug="+collectionAddress

    marketCap = requests.get(url, headers=headers)
    marketCap = json.loads(marketCap.text)
    marketCap = str(marketCap['valuation']) + " ETH"

    print(marketCap)
    return marketCap

#All time, can expand to 1d,7d,1m,3m,6m,1y
def getVolume (collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_volume?contract_address_or_opensea_slug="+collectionAddress+"&duration=1d"

    volume = requests.get(url, headers=headers)
    volume = json.loads(volume.text)
    volume = str(volume['amount']) + " ETH Volume in the last 1d"

    print(volume)
    return volume

#All time, can expand to 1d,7d,1m,3m,6m,1y
def getVolumeSevenDay (collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_volume?contract_address_or_opensea_slug="+collectionAddress+"&duration=7d"

    volume = requests.get(url, headers=headers)
    volume = json.loads(volume.text)
    volume = str(volume['amount']) + " ETH Volume in the last 7d"

    print(volume)
    return volume

#All time, can expand to 1d,7d,1m,3m,6m,1y
def getVolumeMonth (collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_volume?contract_address_or_opensea_slug="+collectionAddress+"&duration=1m"

    volume = requests.get(url, headers=headers)
    volume = json.loads(volume.text)
    volume = str(volume['amount']) + " ETH Volume in the last 1m"

    print(volume)
    return volume

#All time, can expand to 1d,7d,1m,3m,6m,1y
def getVolumeThreeMonth (collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_volume?contract_address_or_opensea_slug="+collectionAddress+"&duration=3m"

    volume = requests.get(url, headers=headers)
    volume = json.loads(volume.text)
    volume = str(volume['amount']) + " ETH Volume in the last 3m"

    print(volume)
    return volume

#All time, can expand to 1d,7d,1m,3m,6m,1y
def getVolumeSixMonth (collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_volume?contract_address_or_opensea_slug="+collectionAddress+"&duration=6m"

    volume = requests.get(url, headers=headers)
    volume = json.loads(volume.text)
    volume = str(volume['amount']) + " ETH Volume in the last 6m"

    print(volume)
    return volume

#All time, can expand to 1d,7d,1m,3m,6m,1y
def getVolumeOneYear(collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_volume?contract_address_or_opensea_slug="+collectionAddress+"&duration=1y"

    volume = requests.get(url, headers=headers)
    volume = json.loads(volume.text)
    volume = str(volume['amount']) + " ETH Volume in the last 1y"

    print(volume)
    return volume

#7 Days, can expand to 1d,7d,1m,3m,6m,1y
def getSalesCount(collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_count?contract_address_or_opensea_slug="+collectionAddress+"&duration=1d"


    salesCount = requests.get(url, headers=headers)
    salesCount = json.loads(salesCount.text)
    salesCount = str(salesCount['count']) + " transacted in the last 1d"

    print(salesCount)
    return salesCount

#7 Days, can expand to 1d,7d,1m,3m,6m,1y
def getSalesCountSevenDay(collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_count?contract_address_or_opensea_slug="+collectionAddress+"&duration=7d"


    salesCount = requests.get(url, headers=headers)
    salesCount = json.loads(salesCount.text)
    salesCount = str(salesCount['count']) + " transacted in the last 7d"

    print(salesCount)
    return salesCount

#7 Days, can expand to 1d,7d,1m,3m,6m,1y
def getSalesCountOneMonth(collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_count?contract_address_or_opensea_slug="+collectionAddress+"&duration=1m"


    salesCount = requests.get(url, headers=headers)
    salesCount = json.loads(salesCount.text)
    salesCount = str(salesCount['count']) + " transacted in the last 1m"

    print(salesCount)
    return salesCount

#7 Days, can expand to 1d,7d,1m,3m,6m,1y
def getSalesCountThreeMonth(collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_count?contract_address_or_opensea_slug="+collectionAddress+"&duration=3m"


    salesCount = requests.get(url, headers=headers)
    salesCount = json.loads(salesCount.text)
    salesCount = str(salesCount['count']) + " transacted in the last 3m"

    print(salesCount)
    return salesCount

#7 Days, can expand to 1d,7d,1m,3m,6m,1y
def getSalesCountSixMonth(collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_count?contract_address_or_opensea_slug="+collectionAddress+"&duration=6m"


    salesCount = requests.get(url, headers=headers)
    salesCount = json.loads(salesCount.text)
    salesCount = str(salesCount['count']) + " transacted in the last 6m"

    print(salesCount)
    return salesCount

#7 Days, can expand to 1d,7d,1m,3m,6m,1y
def getSalesCountOneYear(collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/sales_count?contract_address_or_opensea_slug="+collectionAddress+"&duration=1y"


    salesCount = requests.get(url, headers=headers)
    salesCount = json.loads(salesCount.text)
    salesCount = str(salesCount['count']) + " transacted in the last 1y"

    print(salesCount)
    return salesCount

#Currently returns last sale. Twitter does not allow this to be tweeted for an uknown reason (Likely the amount of slashes - flagged as spam)
def getLatestSales(collectionAddress):
    
    url = "https://api.ebitlabs.com/v1/last_transactions?contract_address_or_opensea_slug="+collectionAddress+"&count=1"

    latestSales = requests.get(url, headers=headers)
    #Currently returns in JSON format as that makes "the most sense" for this use case. Can be modified for something else
    latestSales = json.dumps(latestSales.text)
    print(latestSales)
    return latestSales


commands = ["floor price", "market cap", "volume", "volume 1d", "volume 7d", "volume 1m", "volume 3m", "volume 6m", "volume 1y", "sales count", "sales count 1d", "sales count 7d", "sales count 1m", "sales count 3m", "sales count 6m", "sales count 1y", "latest sales"]

commandFunctions = {
    "floor price": getFloor,
    "market cap": getMarketCap,
    "volume": getVolume,
    "volume 1d": getVolume,
    "volume 7d": getVolumeSevenDay,
    "volume 1m": getVolumeMonth,
    "volume 3m": getVolumeThreeMonth,
    "volume 6m": getVolumeSixMonth,
    "volume 1y": getVolumeOneYear,
    "sales count": getSalesCount,
    "sales count 1d": getSalesCount,
    "sales count 7d": getSalesCountSevenDay,
    "sales count 1m": getSalesCountOneMonth,
    "sales count 3m": getSalesCountThreeMonth,
    "sales count 6m": getSalesCountSixMonth,
    "sales count 1y": getSalesCountOneYear,
    "latest sales": getLatestSales
}

def getCommand (query):
    bestMatch = process.extractOne(query, commands)
    
    if bestMatch[1] < 75:
        return "No command found, check your spelling and try again."
    
    command = bestMatch[0]
    print("Using command: " + command)

    return command

"""" 
Current way to use this: "Collection name + Command"

example: "Azuki - floor price" I can modify this logic to be easier to use, but this is the fastest way to split collection from command

commands: 

floor price
market cap
volume
sales count
latest sales

"""


import tweepy
import time
#Client Id = R2FDR2I1bmxnUHFpekF6SnozTzQ6MTpjaQ
#Client Secret = plfQX4hS5B4ExAN9n6wPL_1wFZOcIA2FLEAGb_CgGrRHqZ_yRF


apiKey = "g6JsWag9bA5RsMYcLhWI1XGBd"
apiSecret = "9jWm5L3qx9htYsKGh59LNLD7EA5tVBxl6l0gk4manHONMRqOir"

bearerToken = "AAAAAAAAAAAAAAAAAAAAALrCpAEAAAAA4Z8eRdEx3Fjb2QtmsfsC8a3WAXw%3DfJMZ5az8Y8HabPozdeZcNfy6oEyo49FjQxlKokMGSuv7r3XChi"
accessToken = "1686671873403133952-qAiQs8bD27Y2yMyoI9yMWdWIrJlHpx"
accessSecret = "DBbi5GBxkKsLy2DZuiuuAItnbMiyC8gaBdyBG7gQdu7xs"

client = tweepy.Client(bearerToken, apiKey, apiSecret, accessToken, accessSecret)
auth = tweepy.OAuth1UserHandler(apiKey, apiSecret, accessToken, accessSecret)
api = tweepy.API(auth,wait_on_rate_limit=True)

clientId = client.get_me().data.id

with open('since_id.txt','r') as fp:
    startId = fp.read()

while True:
    response = client.get_users_mentions(clientId, since_id=startId)
    if response.data != None:
        for tweet in response.data:
            try:
                print(tweet.text)
                collectionTweet, commandTweet = tweet.text.split('-', 1)

                chosenCollectionTweet = getCollection(collectionTweet)
                commandChosenTweet = getCommand(commandTweet)

                tweetCommandFunction = commandFunctions.get(commandChosenTweet)
                message = ''

                print('tweetCommandFunction:',tweetCommandFunction)

                if tweetCommandFunction is None:
                    message = "Invalid command. Please use 'collection name - command'. See Bio for commands. "[:280]
                else:
                    message = tweetCommandFunction(chosenCollectionTweet)[:280]

                message += "\n https://app.tokensite.com/"
                client.create_tweet(in_reply_to_tweet_id=tweet.id, text=message[:280])

            except Exception as e:
                print(f"An error occurred: {e}")
            
            time.sleep(5)
            
        startId = response.meta['newest_id']
        with open('since_id.txt','w') as fp:
            fp.write(startId)
            
    else:
        print('no new tweets')
    time.sleep(60)

            
