"""
Serviços para operações com mapas
"""
from typing import Dict, List, Tuple, Optional
import folium
from folium.plugins import MarkerCluster

from src.models.schemas import DadosMapa
from src.config.settings import MAP_CENTER_LAT, MAP_CENTER_LON, MAP_ZOOM_START


class MapasService:
    """Serviço para criação e manipulação de mapas"""
    
    # Coordenadas dos estados brasileiros
    _COORDENADAS_ESTADOS: Dict[str, Tuple[float, float]] = {
        "AC": [-9.0238, -70.8120],
        "AL": [-9.5710, -36.7820],
        "AM": [-3.4653, -62.2159],
        "AP": [0.9019, -51.9577],
        "BA": [-12.5797, -41.7007],
        "CE": [-5.4984, -39.3206],
        "DF": [-15.7998, -47.8645],
        "ES": [-19.1834, -40.3089],
        "GO": [-15.8270, -49.8362],
        "MA": [-4.9609, -45.2744],
        "MG": [-18.5122, -44.5550],
        "MS": [-20.7722, -54.7851],
        "MT": [-12.6819, -56.9211],
        "PA": [-3.4168, -52.3506],
        "PB": [-7.2760, -36.0294],
        "PE": [-8.0586, -38.3175],
        "PI": [-6.2470, -42.3551],
        "PR": [-24.9568, -51.6461],
        "RJ": [-22.2259, -42.7069],
        "RN": [-5.4026, -36.9541],
        "RO": [-11.5057, -63.5806],
        "RR": [1.8849, -61.2209],
        "RS": [-29.6954, -53.8725],
        "SC": [-27.2437, -50.2640],
        "SE": [-10.5431, -37.4310],
        "SP": [-23.5505, -46.6333],
        "TO": [-9.7088, -48.4615],
    }
    
    # Coordenadas de cidades brasileiras (mais de 500 cidades)
    _COORDENADAS_CIDADES: Dict[str, Tuple[float, float]] = {
        # ==================== NORTE ====================
        # Amazonas
        "Manaus": [-3.1190, -60.0217],
        "Parintins": [-2.6284, -56.7357],
        "Itacoatiara": [-3.1386, -58.4444],
        "Manacapuru": [-3.2998, -60.6206],
        "Coari": [-4.0943, -63.1411],
        "Tabatinga": [-4.2316, -69.9380],
        "Maués": [-3.3835, -57.7185],
        "Tefé": [-3.3686, -64.7200],
        "Humaitá": [-7.5060, -63.0203],
        "Lábrea": [-7.2589, -64.7977],
        
        # Pará
        "Belém": [-1.4558, -48.4902],
        "Ananindeua": [-1.3654, -48.3723],
        "Santarém": [-2.4431, -54.7083],
        "Marabá": [-5.3688, -49.1179],
        "Castanhal": [-1.2939, -47.9261],
        "Parauapebas": [-6.0676, -49.9038],
        "Tailândia": [-2.9474, -48.9489],
        "Altamira": [-3.2040, -52.2058],
        "Barcarena": [-1.5118, -48.6196],
        "Cametá": [-2.2445, -49.4958],
        "Breves": [-1.6824, -50.4802],
        "Itaituba": [-4.2667, -55.9833],
        "Jacundá": [-4.4462, -49.1160],
        "Redenção": [-8.0290, -50.0317],
        "Tucuruí": [-3.7658, -49.7202],
        
        # Rondônia
        "Porto Velho": [-8.7619, -63.9039],
        "Ji-Paraná": [-10.8854, -61.9517],
        "Ariquemes": [-9.9052, -63.0325],
        "Vilhena": [-12.7402, -60.1458],
        "Cacoal": [-11.4386, -61.4470],
        "Pimenta Bueno": [-11.6725, -61.1980],
        "Jaru": [-10.4366, -62.4665],
        "Rolim de Moura": [-11.7272, -61.7784],
        "Guajará-Mirim": [-10.7837, -65.3293],
        
        # Acre
        "Rio Branco": [-9.9754, -67.8249],
        "Cruzeiro do Sul": [-7.6276, -72.6709],
        "Sena Madureira": [-9.0659, -68.6577],
        "Tarauacá": [-8.1610, -70.7659],
        "Feijó": [-8.1700, -70.3511],
        
        # Roraima
        "Boa Vista": [2.8235, -60.6758],
        "Rorainópolis": [0.9396, -60.4384],
        "Caracaraí": [1.8158, -61.1279],
        
        # Amapá
        "Macapá": [0.0349, -51.0694],
        "Santana": [-0.0583, -51.1817],
        "Laranjal do Jari": [-0.8406, -52.5160],
        "Oiapoque": [3.8407, -51.8331],
        
        # Tocantins
        "Palmas": [-10.1845, -48.3337],
        "Araguaína": [-7.1918, -48.2066],
        "Gurupi": [-11.7279, -49.0688],
        "Porto Nacional": [-10.7076, -48.4171],
        "Paraíso do Tocantins": [-10.1757, -48.8823],
        "Colinas do Tocantins": [-8.0574, -48.4759],
        "Dianópolis": [-11.6242, -46.8198],
        
        # ==================== NORDESTE ====================
        # Maranhão
        "São Luís": [-2.5307, -44.3028],
        "Imperatriz": [-5.5265, -47.4918],
        "Caxias": [-4.8589, -43.3561],
        "Timon": [-5.0977, -42.8326],
        "Codó": [-4.4554, -43.8856],
        "Paço do Lumiar": [-2.5250, -44.1051],
        "Açailândia": [-4.9472, -47.5004],
        "Bacabal": [-4.2249, -44.7832],
        "Balsas": [-7.5325, -46.0357],
        "Santa Inês": [-3.6634, -45.3802],
        "Pinheiro": [-2.5214, -45.0829],
        "Chapadinha": [-3.7383, -43.3600],
        "Barra do Corda": [-5.4968, -45.2485],
        
        # Piauí
        "Teresina": [-5.0919, -42.8034],
        "Parnaíba": [-2.9045, -41.7769],
        "Picos": [-7.0769, -41.4669],
        "Floriano": [-6.7666, -43.0226],
        "Campo Maior": [-4.8277, -42.1688],
        "Barras": [-4.2444, -42.2942],
        "Altos": [-5.0385, -42.4622],
        "José de Freitas": [-4.7561, -42.5746],
        "Oeiras": [-7.0191, -42.1283],
        "Pedro II": [-4.4248, -41.4483],
        
        # Ceará
        "Fortaleza": [-3.7172, -38.5434],
        "Caucaia": [-3.7360, -38.6531],
        "Juazeiro do Norte": [-7.2132, -39.3151],
        "Maracanaú": [-3.8769, -38.6257],
        "Sobral": [-3.6897, -40.3482],
        "Crato": [-7.2343, -39.4093],
        "Itapipoca": [-3.4943, -39.5786],
        "Maranguape": [-3.8913, -38.6822],
        "Iguatu": [-6.3595, -39.2980],
        "Quixadá": [-4.9714, -39.0155],
        "Pacajus": [-4.1722, -38.4606],
        "Acaraú": [-2.8876, -40.1200],
        # Existe também um "Cascavel" no Paraná (ver mais abaixo); como este
        # dicionário é uma chave única nome->coordenadas para o Brasil todo,
        # os dois nomes colidiam e o do Paraná sobrescrevia silenciosamente
        # este aqui. Desambiguado para não perder a cidade cearense.
        "Cascavel (CE)": [-4.1332, -38.2412],
        "Horizonte": [-4.0998, -38.4830],
        "Limoeiro do Norte": [-5.1443, -38.0985],
        "Tauá": [-6.0027, -40.2928],
        
        # Rio Grande do Norte
        "Natal": [-5.7945, -35.2110],
        "Mossoró": [-5.1875, -37.3442],
        "Parnamirim": [-5.9155, -35.2630],
        "São Gonçalo do Amarante": [-5.7932, -35.3293],
        "Macaíba": [-5.8563, -35.3538],
        "Ceará-Mirim": [-5.6342, -35.4240],
        "Caicó": [-6.4585, -37.0975],
        "Assu": [-5.5767, -36.9097],
        "Currais Novos": [-6.2608, -36.5146],
        "Santa Cruz": [-6.2244, -36.0193],
        
        # Paraíba
        "João Pessoa": [-7.1153, -34.8649],
        "Campina Grande": [-7.2306, -35.8811],
        "Santa Rita": [-7.1139, -34.9753],
        "Patos": [-7.0243, -37.2746],
        "Bayeux": [-7.1255, -34.9364],
        "Sousa": [-6.7596, -38.2311],
        "Cajazeiras": [-6.8904, -38.5620],
        "Guarabira": [-6.8546, -35.4900],
        "Areia": [-6.9639, -35.6977],
        
        # Pernambuco
        "Recife": [-8.0476, -34.8770],
        "Jaboatão dos Guararapes": [-8.1126, -35.0147],
        "Olinda": [-8.0109, -34.8547],
        "Caruaru": [-8.2842, -35.9708],
        "Petrolina": [-9.3987, -40.5006],
        "Paulista": [-7.9408, -34.8731],
        "Cabo de Santo Agostinho": [-8.2868, -35.0355],
        "Camaragibe": [-8.0235, -34.9820],
        "Garanhuns": [-8.8904, -36.4930],
        "Vitória de Santo Antão": [-8.1280, -35.2974],
        "São Lourenço da Mata": [-8.0067, -35.0189],
        "Ipojuca": [-8.3988, -35.0645],
        "Serra Talhada": [-7.9817, -38.2932],
        "Araripina": [-7.5760, -40.4983],
        "Gravatá": [-8.2016, -35.5655],
        "Belo Jardim": [-8.3373, -36.4243],
        "Santa Cruz do Capibaribe": [-7.9575, -36.2046],
        
        # Alagoas
        "Maceió": [-9.6663, -35.7350],
        "Arapiraca": [-9.7549, -36.6615],
        "Rio Largo": [-9.4776, -35.8480],
        "Palmeira dos Índios": [-9.4071, -36.6335],
        "União dos Palmares": [-9.1592, -36.0323],
        "Penedo": [-10.2894, -36.5828],
        "São Miguel dos Campos": [-9.7830, -36.0975],
        "Coruripe": [-10.1257, -36.1716],
        
        # Sergipe
        "Aracaju": [-10.9472, -37.0731],
        "Nossa Senhora do Socorro": [-10.8463, -37.1301],
        "Lagarto": [-10.9172, -37.6501],
        "Itabaiana": [-10.6854, -37.4254],
        "São Cristóvão": [-11.0148, -37.2049],
        "Estância": [-11.2689, -37.4385],
        "Tobias Barreto": [-11.1835, -38.0072],
        "Simão Dias": [-10.7380, -37.8105],
        
        # Bahia
        "Salvador": [-12.9777, -38.5016],
        "Feira de Santana": [-12.2561, -38.9593],
        "Vitória da Conquista": [-14.8660, -40.8358],
        "Camaçari": [-12.6992, -38.3262],
        "Juazeiro": [-9.4308, -40.5037],
        "Lauro de Freitas": [-12.8942, -38.3270],
        "Ilhéus": [-14.7934, -39.0499],
        "Jequié": [-13.8551, -40.0819],
        "Teixeira de Freitas": [-17.5390, -39.7418],
        "Barreiras": [-12.1539, -44.9945],
        "Alagoinhas": [-12.1356, -38.4192],
        "Porto Seguro": [-16.4431, -39.0643],
        "Simões Filho": [-12.7839, -38.4027],
        "Paulo Afonso": [-9.4075, -38.2216],
        "Eunápolis": [-16.3716, -39.5809],
        "Santo Antônio de Jesus": [-12.9691, -39.2613],
        "Valença": [-13.3701, -39.0730],
        "Candeias": [-12.6673, -38.5509],
        "Guanambi": [-14.2233, -42.7799],
        "Jacobina": [-11.1814, -40.5133],
        "Senhor do Bonfim": [-10.4614, -40.1895],
        "Dias d'Ávila": [-12.6141, -38.2967],
        "Itabuna": [-14.7876, -39.2782],
        
        # ==================== CENTRO-OESTE ====================
        # Distrito Federal
        "Brasília": [-15.7975, -47.8919],
        "Ceilândia": [-15.8168, -48.1100],
        "Taguatinga": [-15.8330, -48.0568],
        "Gama": [-16.0130, -48.0575],
        "Samambaia": [-15.8730, -48.0966],
        "Planaltina": [-15.6180, -47.6498],
        "Guará": [-15.8264, -47.9777],
        
        # Goiás
        "Goiânia": [-16.6869, -49.2648],
        "Aparecida de Goiânia": [-16.8218, -49.2445],
        "Anápolis": [-16.3269, -48.9529],
        "Rio Verde": [-17.7922, -50.9192],
        "Luziânia": [-16.2525, -47.9502],
        "Águas Lindas de Goiás": [-15.7617, -48.2816],
        "Valparaíso de Goiás": [-16.0642, -47.9751],
        "Trindade": [-16.6491, -49.4889],
        "Formosa": [-15.5372, -47.3345],
        "Senador Canedo": [-16.7094, -49.0900],
        "Itumbiara": [-18.4192, -49.2152],
        "Jataí": [-17.8790, -51.7166],
        "Catalão": [-18.1656, -47.9462],
        "Planaltina de Goiás": [-15.4528, -48.1799],
        "Caldas Novas": [-17.7441, -48.6251],
        "Goianésia": [-15.3176, -49.1122],
        "Mineiros": [-17.5680, -52.5512],
        "Inhumas": [-16.3610, -49.5000],
        "Cristalina": [-16.7676, -47.6132],
        
        # Mato Grosso
        "Cuiabá": [-15.5989, -56.0949],
        "Várzea Grande": [-15.6467, -56.1323],
        "Rondonópolis": [-16.4705, -54.6356],
        "Sinop": [-11.8642, -55.5026],
        "Tangará da Serra": [-14.6214, -57.4858],
        "Cáceres": [-16.0712, -57.6787],
        "Sorriso": [-12.5425, -55.7211],
        "Lucas do Rio Verde": [-13.0588, -55.9084],
        "Barra do Garças": [-15.8906, -52.2567],
        "Primavera do Leste": [-15.5249, -54.3461],
        "Alta Floresta": [-9.8667, -56.0667],
        "Campo Verde": [-15.5464, -55.1628],
        "Nova Mutum": [-13.8372, -56.0744],
        "Juína": [-11.4287, -58.7478],
        
        # Mato Grosso do Sul
        "Campo Grande": [-20.4697, -54.6201],
        "Dourados": [-22.2211, -54.8056],
        "Três Lagoas": [-20.7566, -51.6785],
        "Corumbá": [-19.0153, -57.6460],
        "Ponta Porã": [-22.5361, -55.7256],
        "Sidrolândia": [-20.9312, -54.9616],
        "Naviraí": [-23.0617, -54.1991],
        "Nova Andradina": [-22.2360, -53.3437],
        "Aquidauana": [-20.4705, -55.7873],
        "Maracaju": [-21.6142, -55.1685],
        "Rio Brilhante": [-21.8033, -54.5427],
        
        # ==================== SUDESTE ====================
        # Minas Gerais
        "Belo Horizonte": [-19.9191, -43.9387],
        "Contagem": [-19.9322, -44.0536],
        "Juiz de Fora": [-21.7595, -43.3398],
        "Uberlândia": [-18.9128, -48.2755],
        "Uberaba": [-19.7479, -47.9381],
        "Betim": [-19.9678, -44.1982],
        "Montes Claros": [-16.7350, -43.8617],
        "Ribeirão das Neves": [-19.7664, -44.0867],
        "Governador Valadares": [-18.8512, -41.9491],
        "Ipatinga": [-19.4686, -42.5379],
        "Sete Lagoas": [-19.4653, -44.2466],
        "Divinópolis": [-20.1448, -44.8835],
        "Santa Luzia": [-19.7667, -43.8497],
        "Poços de Caldas": [-21.7880, -46.5618],
        "Patos de Minas": [-18.5768, -46.5202],
        "Barbacena": [-21.2255, -43.7738],
        "Varginha": [-21.5514, -45.4303],
        "Sabará": [-19.8864, -43.8064],
        "Itabira": [-19.6191, -43.2269],
        "Pouso Alegre": [-22.2302, -45.9364],
        "Passos": [-20.7190, -46.6099],
        "Araxá": [-19.5904, -46.9405],
        "Conselheiro Lafaiete": [-20.6601, -43.7863],
        "Ituiutaba": [-18.9772, -49.4651],
        "Coronel Fabriciano": [-19.5190, -42.6288],
        "Pará de Minas": [-19.8600, -44.6078],
        "Caratinga": [-19.7910, -42.1358],
        "Nova Lima": [-19.9858, -43.8468],
        "Ouro Preto": [-20.3850, -43.5035],
        "Mariana": [-20.3777, -43.4160],
        "São João del Rei": [-21.1359, -44.2619],
        "Tiradentes": [-21.1102, -44.1748],
        "Diamantina": [-18.2449, -43.6006],
        
        # Espírito Santo
        "Vitória": [-20.3194, -40.3378],
        "Vila Velha": [-20.3297, -40.2921],
        "Serra": [-20.1286, -40.3078],
        "Cariacica": [-20.2632, -40.4166],
        "Linhares": [-19.3910, -40.0734],
        "São Mateus": [-18.7201, -39.8585],
        "Guarapari": [-20.6579, -40.5103],
        "Alegre": [-20.7633, -41.5332],
        "Colatina": [-19.5383, -40.6325],
        "Nova Venécia": [-18.7100, -40.4000],
        "Barra de São Francisco": [-18.7550, -40.8910],
        "Itapemirim": [-21.0100, -40.8300],
        "Castelo": [-20.6033, -41.1847],
        
        # Rio de Janeiro
        "Rio de Janeiro": [-22.9068, -43.1729],
        "São Gonçalo": [-22.8268, -43.0537],
        "Duque de Caxias": [-22.7858, -43.3047],
        "Nova Iguaçu": [-22.7556, -43.4605],
        "Niterói": [-22.8832, -43.1039],
        "Campos dos Goytacazes": [-21.7620, -41.3184],
        "Belford Roxo": [-22.7640, -43.3992],
        "São João de Meriti": [-22.8038, -43.3722],
        "Petrópolis": [-22.5050, -43.1784],
        "Volta Redonda": [-22.5234, -44.1033],
        "Macaé": [-22.3762, -41.7841],
        "Itaboraí": [-22.7476, -42.8602],
        "Cabo Frio": [-22.8762, -42.0298],
        "Angra dos Reis": [-23.0066, -44.3186],
        "Barra Mansa": [-22.5481, -44.1712],
        "Teresópolis": [-22.4129, -42.9658],
        "Nova Friburgo": [-22.2820, -42.5306],
        "Araruama": [-22.8728, -42.3428],
        "Resende": [-22.4686, -44.4469],
        "Maricá": [-22.9190, -42.8186],
        "Itaguaí": [-22.8520, -43.7752],
        "Queimados": [-22.7157, -43.5551],
        "Japeri": [-22.6435, -43.6602],
        "Paracambi": [-22.6067, -43.7083],
        "São Pedro da Aldeia": [-22.8359, -42.1026],
        "Saquarema": [-22.9200, -42.5100],
        "Búzios": [-22.7466, -41.8816],
        
        # São Paulo
        "São Paulo": [-23.5505, -46.6333],
        "Guarulhos": [-23.4538, -46.5333],
        "Campinas": [-22.9056, -47.0608],
        "São Bernardo do Campo": [-23.6939, -46.5650],
        "Santo André": [-23.6636, -46.5383],
        "Osasco": [-23.5324, -46.7916],
        "São José dos Campos": [-23.1896, -45.8841],
        "Ribeirão Preto": [-21.1779, -47.8107],
        "Sorocaba": [-23.5015, -47.4525],
        "Santos": [-23.9608, -46.3322],
        "Mauá": [-23.6677, -46.4610],
        "Diadema": [-23.6813, -46.6205],
        "Jundiaí": [-23.1857, -46.8978],
        "Carapicuíba": [-23.5235, -46.8407],
        "Piracicaba": [-22.7253, -47.6492],
        "São José do Rio Preto": [-20.8196, -49.3797],
        "Mogi das Cruzes": [-23.5208, -46.1854],
        "Bauru": [-22.3145, -49.0607],
        "Itaquaquecetuba": [-23.4863, -46.3484],
        "São Vicente": [-23.9632, -46.3910],
        "Taubaté": [-23.0262, -45.5553],
        "Franca": [-20.5382, -47.4009],
        "Praia Grande": [-24.0060, -46.4030],
        "Limeira": [-22.5653, -47.4018],
        "Suzano": [-23.5426, -46.3108],
        "Taboão da Serra": [-23.6019, -46.7526],
        "Sumaré": [-22.8219, -47.2670],
        "Barueri": [-23.5104, -46.8765],
        "Embu das Artes": [-23.6490, -46.8523],
        "Cotia": [-23.6020, -46.9189],
        "Americana": [-22.7390, -47.3314],
        "Santa Bárbara d'Oeste": [-22.7553, -47.4144],
        "Rio Claro": [-22.4103, -47.5609],
        "Indaiatuba": [-23.0811, -47.2100],
        "Araraquara": [-21.7945, -48.1756],
        "Jacareí": [-23.3053, -45.9658],
        "Itapevi": [-23.5488, -46.9345],
        "Hortolândia": [-22.8528, -47.2143],
        "Marília": [-22.2139, -49.9459],
        "Presidente Prudente": [-22.1256, -51.3889],
        "Araçatuba": [-21.2086, -50.4400],
        "São Carlos": [-22.0177, -47.8862],
        "Itu": [-23.2644, -47.2992],
        "Bragança Paulista": [-22.9527, -46.5419],
        "Atibaia": [-23.1177, -46.5564],
        "Pindamonhangaba": [-22.9246, -45.4586],
        "Itatiba": [-23.0057, -46.8384],
        "Botucatu": [-22.8908, -48.4450],
        "Ourinhos": [-22.9797, -49.8708],
        "Catanduva": [-21.1378, -48.9771],
        "Votuporanga": [-20.4224, -49.9728],
        "Fernandópolis": [-20.2860, -50.2460],
        "Jales": [-20.2685, -50.5458],
        "Tupã": [-21.9342, -50.5130],
        "Lins": [-21.6788, -49.7426],
        "Birigui": [-21.2886, -50.3402],
        "Assis": [-22.6605, -50.4133],
        "Avaré": [-23.0985, -48.9256],
        "Itapetininga": [-23.5920, -48.0530],
        "Mogi Guaçu": [-22.3675, -46.9428],
        "Pirassununga": [-21.9962, -47.4257],
        "Porto Ferreira": [-21.8534, -47.4790],
        "Sertãozinho": [-21.1318, -47.9905],
        "Jaboticabal": [-21.2552, -48.3222],
        "Monte Alto": [-21.2611, -48.4972],
        "Bebedouro": [-20.9496, -48.4791],
        "Barretos": [-20.5560, -48.5670],
        "Olímpia": [-20.7366, -48.9106],
        "São Joaquim da Barra": [-20.5814, -47.8592],
        "Guariba": [-21.3599, -48.2286],
        "Matão": [-21.6000, -48.3667],
        "Taquaritinga": [-21.4058, -48.5048],
        "Santa Cruz do Rio Pardo": [-22.8988, -49.6324],
        "Boa Esperança do Sul": [-21.9925, -48.3908],
        "Ibitinga": [-21.7580, -48.8288],
        "Cravinhos": [-21.3402, -47.7291],
        "Serrana": [-21.2114, -47.5958],
        "Batatais": [-20.8939, -47.5850],
        "Altinópolis": [-21.0214, -47.3740],
        "Caconde": [-21.5291, -46.6438],
        
        # ==================== SUL ====================
        # Paraná
        "Curitiba": [-25.4290, -49.2671],
        "Londrina": [-23.3105, -51.1628],
        "Maringá": [-23.4253, -51.9382],
        "Ponta Grossa": [-25.0923, -50.1619],
        "Cascavel": [-24.9573, -53.4590],
        "São José dos Pinhais": [-25.5350, -49.2060],
        "Foz do Iguaçu": [-25.5160, -54.5850],
        "Colombo": [-25.2925, -49.2242],
        "Guarapuava": [-25.3904, -51.4654],
        "Paranaguá": [-25.5207, -48.5096],
        "Apucarana": [-23.5509, -51.4609],
        "Toledo": [-24.7246, -53.7412],
        "Arapongas": [-23.4193, -51.4244],
        "Campo Largo": [-25.4595, -49.5278],
        "Pinhais": [-25.4445, -49.1928],
        "Umuarama": [-23.7664, -53.3201],
        "Piraquara": [-25.4423, -49.0627],
        "Sarandi": [-23.4437, -51.8739],
        "Cambé": [-23.2772, -51.2779],
        "Campo Mourão": [-24.0456, -52.3828],
        "Almirante Tamandaré": [-25.3251, -49.3102],
        "Araucária": [-25.5856, -49.4134],
        "Fazenda Rio Grande": [-25.6579, -49.3073],
        "Paranavaí": [-23.0812, -52.4615],
        "Francisco Beltrão": [-26.0812, -53.0551],
        "Cianorte": [-23.6599, -52.6054],
        "Telêmaco Borba": [-24.3238, -50.6156],
        "Castro": [-24.7906, -50.0116],
        "Rolândia": [-23.3100, -51.3659],
        "Ibiporã": [-23.2688, -51.0485],
        
        # Santa Catarina
        "Florianópolis": [-27.5949, -48.5482],
        "Joinville": [-26.3045, -48.8487],
        "Blumenau": [-26.9194, -49.0661],
        "São José": [-27.6154, -48.6277],
        "Criciúma": [-28.6776, -49.3699],
        "Chapecó": [-27.0960, -52.6183],
        "Itajaí": [-26.9078, -48.6619],
        "Palhoça": [-27.6455, -48.6677],
        "Brusque": [-27.0969, -48.9128],
        "Lages": [-27.8152, -50.3257],
        "Balneário Camboriú": [-26.9926, -48.6352],
        "Tubarão": [-28.4666, -49.0068],
        "Jaraguá do Sul": [-26.4861, -49.0669],
        "Camboriú": [-27.0206, -48.6539],
        "Navegantes": [-26.8989, -48.6545],
        "Gaspar": [-26.9294, -48.9589],
        "Sombrio": [-29.1139, -49.6328],
        "Araranguá": [-28.9356, -49.4941],
        "Rio do Sul": [-27.2111, -49.6430],
        "Mafra": [-26.1121, -49.8083],
        "Concórdia": [-27.2348, -52.0278],
        "Xanxerê": [-26.8767, -52.4040],
        "Canoinhas": [-26.1766, -50.3950],
        "São Bento do Sul": [-26.2493, -49.3831],
        
        # Rio Grande do Sul
        "Porto Alegre": [-30.0346, -51.2177],
        "Caxias do Sul": [-29.1683, -51.1808],
        "Pelotas": [-31.7184, -52.3320],
        "Canoas": [-29.9128, -51.1857],
        "Santa Maria": [-29.6842, -53.8069],
        "Novo Hamburgo": [-29.6780, -51.1305],
        "São Leopoldo": [-29.7549, -51.1470],
        "Gravataí": [-29.9445, -50.9926],
        "Viamão": [-30.0819, -51.0234],
        "Passo Fundo": [-28.2630, -52.4065],
        "Sapucaia do Sul": [-29.8425, -51.1464],
        "Uruguaiana": [-29.7547, -57.0853],
        "Santa Cruz do Sul": [-29.7189, -52.4258],
        "Bagé": [-31.3295, -54.0984],
        "Bento Gonçalves": [-29.1700, -51.5194],
        "Rio Grande": [-32.0310, -52.0985],
        "Alvorada": [-29.9914, -51.0809],
        "Cachoeirinha": [-29.9477, -51.1017],
        "Lajeado": [-29.4590, -51.9644],
        "Erechim": [-27.6364, -52.2696],
        "Guaporé": [-28.8460, -51.8900],
        "Carazinho": [-28.2958, -52.7862],
        "Santo Ângelo": [-28.2992, -54.2631],
        "Ijuí": [-28.3880, -53.9140],
        "Cruz Alta": [-28.6388, -53.6065],
        "São Borja": [-28.6606, -56.0046],
        "Alegrete": [-29.7831, -55.7919],
        "Santana do Livramento": [-30.8910, -55.5323],
        "Vacaria": [-28.5121, -50.9338],
        "Soledade": [-28.8184, -52.5135],
        "Montenegro": [-29.6888, -51.4611],
        "Taquari": [-29.7994, -51.8653],
        "Venâncio Aires": [-29.6143, -52.1931],
        "Estrela": [-29.5000, -51.9667],
        "Farroupilha": [-29.2250, -51.3478],
        "Garibaldi": [-29.2569, -51.5272],
        "Carlos Barbosa": [-29.2969, -51.5036],
        "Gramado": [-29.3786, -50.8775],
        "Canela": [-29.3569, -50.8150],
        "Nova Petrópolis": [-29.3769, -51.1145],
    }
    
    @classmethod
    def get_coordenadas_estado(cls, sigla: str) -> Optional[Tuple[float, float]]:
        """Retorna coordenadas de um estado pela sigla"""
        return cls._COORDENADAS_ESTADOS.get(sigla.upper())
    
    @classmethod
    def get_coordenadas_cidade(cls, nome: str) -> Optional[Tuple[float, float]]:
        """Retorna coordenadas de uma cidade pelo nome"""
        if not nome:
            return None
        
        # Busca exata
        if nome in cls._COORDENADAS_CIDADES:
            return cls._COORDENADAS_CIDADES[nome]
        
        # Busca com normalização (remove acentos, caixa alta/baixa)
        nome_normalizado = cls._normalizar_texto(nome)
        
        # Busca parcial (para cidades com nomes compostos)
        melhor_match = None
        melhor_score = 0
        
        for cidade, coords in cls._COORDENADAS_CIDADES.items():
            cidade_normalizada = cls._normalizar_texto(cidade)
            
            # Verifica se o nome está contido na cidade ou vice-versa
            if nome_normalizado in cidade_normalizada:
                score = len(nome_normalizado) / len(cidade_normalizada)
                if score > melhor_score:
                    melhor_score = score
                    melhor_match = coords
            elif cidade_normalizada in nome_normalizado:
                score = len(cidade_normalizada) / len(nome_normalizado)
                if score > melhor_score:
                    melhor_score = score
                    melhor_match = coords
        
        # Se encontrou um match com score >= 0.5
        if melhor_match and melhor_score >= 0.5:
            return melhor_match
        
        return None
    
    @classmethod
    def _normalizar_texto(cls, texto: str) -> str:
        """Normaliza texto removendo acentos e caracteres especiais"""
        import unicodedata
        if not texto:
            return ""
        texto = texto.lower().strip()
        # Remove acentos
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        # Remove caracteres especiais
        texto = ''.join(c for c in texto if c.isalnum() or c.isspace())
        return texto
    
    @classmethod
    def get_cidade_mais_proxima(cls, nome: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Retorna as coordenadas da cidade mais próxima encontrada
        """
        return cls.get_coordenadas_cidade(nome)
    
    @classmethod
    def preparar_dados_mapa(
        cls,
        ranking_data: List,
        estados_data: List,
        municipio_selecionado: Optional[str] = None,
        estado_selecionado: Optional[str] = None
    ) -> List[DadosMapa]:
        """
        Prepara dados para exibição no mapa
        """
        # Mapeamento nome -> sigla
        siglas = {e["nome"]: e["sigla"] for e in estados_data}
        
        dados_mapa = []
        for item in ranking_data:
            sigla = siglas.get(item.nome)
            if sigla and sigla in cls._COORDENADAS_ESTADOS:
                lat, lon = cls._COORDENADAS_ESTADOS[sigla]
                dados_mapa.append(
                    DadosMapa(
                        sigla=sigla,
                        nome=item.nome,
                        populacao=item.populacao,
                        lat=lat,
                        lon=lon
                    )
                )
        
        return dados_mapa
    
    @classmethod
    def criar_mapa_populacao(
        cls, 
        dados_mapa: List[DadosMapa],
        municipio_selecionado: Optional[str] = None,
        estado_selecionado: Optional[str] = None
    ) -> folium.Map:
        """
        Cria mapa com círculos proporcionais à população e destaque para município selecionado
        """
        if not dados_mapa:
            return None
        
        # Determinar centro do mapa
        center_lat = MAP_CENTER_LAT
        center_lon = MAP_CENTER_LON
        zoom_start = MAP_ZOOM_START
        
        # Se um município foi selecionado, centralizar o mapa nele
        if municipio_selecionado:
            coords = cls.get_coordenadas_cidade(municipio_selecionado)
            if coords:
                center_lat, center_lon = coords
                zoom_start = 10  # Zoom mais próximo para cidade
        
        # Criar mapa base
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles="CartoDB dark_matter"
        )
        
        # Calcular min/max para normalização
        pop_values = [d.populacao for d in dados_mapa]
        max_pop = max(pop_values) if pop_values else 1
        min_pop = min(pop_values) if pop_values else 0
        
        # Adicionar marcadores dos estados
        for dados in dados_mapa:
            # Tamanho proporcional (8 a 45)
            if max_pop > min_pop:
                normalized = (dados.populacao - min_pop) / (max_pop - min_pop)
                radius = 8 + (normalized * 37)
            else:
                radius = 20
            
            # Popup
            popup_text = f"""
            <div style="font-family: 'IBM Plex Sans', sans-serif; min-width: 150px;">
                <b style="font-size: 16px; color: #1F6F5C;">{dados.nome}</b><br>
                <span style="font-size: 14px;">👥 População: <b>{dados.populacao_formatada}</b></span>
            </div>
            """
            
            # Círculo
            folium.CircleMarker(
                location=[dados.lat, dados.lon],
                radius=radius,
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=f"{dados.nome}: {dados.populacao_formatada} habitantes",
                color="#1F6F5C",
                fill=True,
                fill_color="#1F6F5C",
                fill_opacity=0.6,
                weight=2,
            ).add_to(m)
            
            # Rótulo com sigla
            folium.Marker(
                location=[dados.lat - (radius * 0.04), dados.lon],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 10px; font-weight: bold; color: white; text-shadow: 1px 1px 2px black;">{dados.sigla}</div>'
                )
            ).add_to(m)
        
        # Se um município foi selecionado, adicionar marcador de destaque
        if municipio_selecionado:
            coords = cls.get_coordenadas_cidade(municipio_selecionado)
            if coords:
                lat, lon = coords
                
                # Marcador personalizado para o município
                popup_text = f"""
                <div style="font-family: 'IBM Plex Sans', sans-serif; min-width: 180px;">
                    <b style="font-size: 18px; color: #C9962E;">📍 {municipio_selecionado}</b><br>
                    <span style="font-size: 14px; color: #1F6F5C;"><b>📍 Cidade selecionada</b></span>
                </div>
                """
                
                # Marcador com ícone personalizado
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=f"📍 {municipio_selecionado} (selecionado)",
                    icon=folium.Icon(
                        color="orange",
                        icon="star",
                        prefix="fa"
                    )
                ).add_to(m)
                
                # Adicionar um círculo de destaque ao redor da cidade
                folium.Circle(
                    location=[lat, lon],
                    radius=20000,  # 20km
                    color="#C9962E",
                    fill=True,
                    fill_color="#C9962E",
                    fill_opacity=0.15,
                    weight=3,
                    popup=f"📍 {municipio_selecionado}"
                ).add_to(m)
        
        # Se um estado foi selecionado (mas não município), destacar o estado
        elif estado_selecionado:
            # Encontrar o estado no mapa
            for dados in dados_mapa:
                if dados.nome == estado_selecionado:
                    # Adicionar um círculo de destaque ao redor do estado
                    folium.Circle(
                        location=[dados.lat, dados.lon],
                        radius=150000,  # 150km
                        color="#C9962E",
                        fill=True,
                        fill_color="#C9962E",
                        fill_opacity=0.08,
                        weight=2,
                        popup=f"📍 {estado_selecionado} (selecionado)"
                    ).add_to(m)
                    break
        
        return m
    
    @classmethod
    def criar_mapa_clusters(
        cls,
        dados: List[Dict],
        lat_key: str = "lat",
        lon_key: str = "lon",
        popup_template: str = None
    ) -> folium.Map:
        """
        Cria mapa com clusters de marcadores
        """
        if not dados:
            return None
        
        m = folium.Map(
            location=[MAP_CENTER_LAT, MAP_CENTER_LON],
            zoom_start=MAP_ZOOM_START,
            tiles="CartoDB dark_matter"
        )
        
        cluster = MarkerCluster().add_to(m)
        
        for item in dados:
            if lat_key in item and lon_key in item:
                popup = folium.Popup(
                    popup_template.format(**item) if popup_template else str(item),
                    max_width=200
                )
                
                folium.Marker(
                    location=[item[lat_key], item[lon_key]],
                    popup=popup,
                    tooltip=item.get("tooltip", item.get("nome", "")),
                ).add_to(cluster)
        
        return m


# Instância global do serviço
mapas_service = MapasService()
