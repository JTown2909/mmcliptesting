-- mm_ace_watch.lua -- BizHawk (N64, Mupen64Plus core) heap viewer + Link angle watches
-- for Majora's Mask ACE / credits-warp research.
--
-- Load via Tools > Lua Console > Script > Open Script.
-- Defaults are for JP 1.0 / 1.1 (0x30-byte arena nodes). Set NODE_SIZE = 0x10 for US/EU.
-- Addresses are found by scanning RAM for heap nodes, so nothing is hard-coded per version.

local NODE_SIZE   = 0x30
local DOMAIN      = "RDRAM"
local REFRESH     = 5      -- frames between heap list refreshes
local SCAN_START  = 0x200000
local SCAN_END    = 0x800000

local ACTOR_NAMES = {
  [0x000]="Player",
  [0x001]="En_Test",
  [0x002]="En_GirlA",
  [0x003]="En_Part",
  [0x004]="En_Light",
  [0x005]="En_Door",
  [0x006]="En_Box",
  [0x007]="En_Pametfrog",
  [0x008]="En_Okuta",
  [0x009]="En_Bom",
  [0x00A]="En_Wallmas",
  [0x00B]="En_Dodongo",
  [0x00C]="En_Firefly",
  [0x00D]="En_Horse",
  [0x00E]="En_Item00",
  [0x00F]="En_Arrow",
  [0x010]="En_Elf",
  [0x011]="En_Niw",
  [0x012]="En_Tite",
  [0x014]="En_Peehat",
  [0x015]="En_Butte",
  [0x016]="En_Insect",
  [0x017]="En_Fish",
  [0x018]="En_Holl",
  [0x019]="En_Dinofos",
  [0x01A]="En_Hata",
  [0x01B]="En_Zl1",
  [0x01C]="En_Viewer",
  [0x01D]="En_Bubble",
  [0x01E]="Door_Shutter",
  [0x020]="En_Boom",
  [0x021]="En_Torch2",
  [0x022]="En_Minifrog",
  [0x024]="En_St",
  [0x026]="En_A_Obj",
  [0x027]="Obj_Wturn",
  [0x028]="En_River_Sound",
  [0x02A]="En_Ossan",
  [0x02D]="En_Famos",
  [0x02F]="En_Bombf",
  [0x032]="En_Am",
  [0x033]="En_Dekubaba",
  [0x034]="En_M_Fire1",
  [0x035]="En_M_Thunder",
  [0x036]="Bg_Breakwall",
  [0x038]="Door_Warp1",
  [0x039]="Obj_Syokudai",
  [0x03A]="Item_B_Heart",
  [0x03B]="En_Dekunuts",
  [0x03C]="En_Bbfall",
  [0x03D]="Arms_Hook",
  [0x03E]="En_Bb",
  [0x03F]="Bg_Keikoku_Spr",
  [0x041]="En_Wood02",
  [0x043]="En_Death",
  [0x044]="En_Minideath",
  [0x047]="En_Vm",
  [0x048]="Demo_Effect",
  [0x049]="Demo_Kankyo",
  [0x04A]="En_Floormas",
  [0x04C]="En_Rd",
  [0x04D]="Bg_F40_Flift",
  [0x04E]="Bg_Heavy_Block",
  [0x04F]="Obj_Mure",
  [0x050]="En_Sw",
  [0x051]="Object_Kankyo",
  [0x054]="En_Horse_Link_Child",
  [0x055]="Door_Ana",
  [0x05B]="En_Encount1",
  [0x05C]="Demo_Tre_Lgt",
  [0x05F]="En_Encount2",
  [0x060]="En_Fire_Rock",
  [0x061]="Bg_Ctower_Rot",
  [0x062]="Mir_Ray",
  [0x064]="En_Sb",
  [0x065]="En_Bigslime",
  [0x066]="En_Karebaba",
  [0x067]="En_In",
  [0x069]="En_Ru",
  [0x06A]="En_Bom_Chu",
  [0x06B]="En_Horse_Game_Check",
  [0x06C]="En_Rr",
  [0x073]="En_Fr",
  [0x079]="En_Fishing",
  [0x07A]="Obj_Oshihiki",
  [0x07B]="Eff_Dust",
  [0x07C]="Bg_Umajump",
  [0x07D]="Arrow_Fire",
  [0x07E]="Arrow_Ice",
  [0x07F]="Arrow_Light",
  [0x080]="Item_Etcetera",
  [0x081]="Obj_Kibako",
  [0x082]="Obj_Tsubo",
  [0x084]="En_Ik",
  [0x089]="Demo_Shd",
  [0x08A]="En_Dns",
  [0x08B]="Elf_Msg",
  [0x08C]="En_Honotrap",
  [0x08D]="En_Tubo_Trap",
  [0x08E]="Obj_Ice_Poly",
  [0x08F]="En_Fz",
  [0x090]="En_Kusa",
  [0x091]="Obj_Bean",
  [0x092]="Obj_Bombiwa",
  [0x093]="Obj_Switch",
  [0x095]="Obj_Lift",
  [0x096]="Obj_Hsblock",
  [0x097]="En_Okarina_Tag",
  [0x099]="En_Goroiwa",
  [0x09C]="En_Daiku",
  [0x09D]="En_Nwc",
  [0x09E]="Item_Inbox",
  [0x09F]="En_Ge1",
  [0x0A0]="Obj_Blockstop",
  [0x0A1]="En_Sda",
  [0x0A2]="En_Clear_Tag",
  [0x0A4]="En_Gm",
  [0x0A5]="En_Ms",
  [0x0A6]="En_Hs",
  [0x0A7]="Bg_Ingate",
  [0x0A8]="En_Kanban",
  [0x0AA]="En_Attack_Niw",
  [0x0AE]="En_Mk",
  [0x0AF]="En_Owl",
  [0x0B0]="En_Ishi",
  [0x0B1]="Obj_Hana",
  [0x0B2]="Obj_Lightswitch",
  [0x0B3]="Obj_Mure2",
  [0x0B5]="En_Fu",
  [0x0B8]="En_Stream",
  [0x0B9]="En_Mm",
  [0x0BC]="En_Weather_Tag",
  [0x0BD]="En_Ani",
  [0x0BF]="En_Js",
  [0x0C4]="En_Okarina_Effect",
  [0x0C5]="En_Mag",
  [0x0C6]="Elf_Msg2",
  [0x0C7]="Bg_F40_Swlift",
  [0x0CA]="En_Kakasi",
  [0x0CB]="Obj_Makeoshihiki",
  [0x0CC]="Oceff_Spot",
  [0x0CE]="En_Torch",
  [0x0D0]="Shot_Sun",
  [0x0D3]="Obj_Roomtimer",
  [0x0D4]="En_Ssh",
  [0x0D6]="Oceff_Wipe",
  [0x0D7]="Oceff_Storm",
  [0x0D8]="Obj_Demo",
  [0x0D9]="En_Minislime",
  [0x0DA]="En_Nutsball",
  [0x0DF]="Oceff_Wipe2",
  [0x0E0]="Oceff_Wipe3",
  [0x0E2]="En_Dg",
  [0x0E3]="En_Si",
  [0x0E4]="Obj_Comb",
  [0x0E5]="Obj_Kibako2",
  [0x0E7]="En_Hs2",
  [0x0E8]="Obj_Mure3",
  [0x0E9]="En_Tg",
  [0x0EC]="En_Wf",
  [0x0ED]="En_Skb",
  [0x0EF]="En_Gs",
  [0x0F0]="Obj_Sound",
  [0x0F1]="En_Crow",
  [0x0F3]="En_Cow",
  [0x0F6]="Oceff_Wipe4",
  [0x0F8]="En_Zo",
  [0x0F9]="Obj_Makekinsuta",
  [0x0FA]="En_Ge3",
  [0x0FC]="Obj_Hamishi",
  [0x0FD]="En_Zl4",
  [0x0FE]="En_Mm2",
  [0x100]="Door_Spiral",
  [0x102]="Obj_Pzlblock",
  [0x103]="Obj_Toge",
  [0x105]="Obj_Armos",
  [0x106]="Obj_Boyo",
  [0x109]="En_Grasshopper",
  [0x10B]="Obj_Grass",
  [0x10C]="Obj_Grass_Carry",
  [0x10D]="Obj_Grass_Unit",
  [0x110]="Bg_Fire_Wall",
  [0x111]="En_Bu",
  [0x112]="En_Encount3",
  [0x113]="En_Jso",
  [0x114]="Obj_Chikuwa",
  [0x115]="En_Knight",
  [0x116]="En_Warp_tag",
  [0x117]="En_Aob_01",
  [0x118]="En_Boj_01",
  [0x119]="En_Boj_02",
  [0x11A]="En_Boj_03",
  [0x11B]="En_Encount4",
  [0x11C]="En_Bom_Bowl_Man",
  [0x11D]="En_Syateki_Man",
  [0x11F]="Bg_Icicle",
  [0x120]="En_Syateki_Crow",
  [0x121]="En_Boj_04",
  [0x122]="En_Cne_01",
  [0x123]="En_Bba_01",
  [0x124]="En_Bji_01",
  [0x125]="Bg_Spdweb",
  [0x128]="En_Mt_tag",
  [0x129]="Boss_01",
  [0x12A]="Boss_02",
  [0x12B]="Boss_03",
  [0x12C]="Boss_04",
  [0x12D]="Boss_05",
  [0x12E]="Boss_06",
  [0x12F]="Boss_07",
  [0x130]="Bg_Dy_Yoseizo",
  [0x132]="En_Boj_05",
  [0x135]="En_Sob1",
  [0x138]="En_Go",
  [0x13A]="En_Raf",
  [0x13B]="Obj_Funen",
  [0x13C]="Obj_Raillift",
  [0x13D]="Bg_Numa_Hana",
  [0x13E]="Obj_Flowerpot",
  [0x13F]="Obj_Spinyroll",
  [0x140]="Dm_Hina",
  [0x141]="En_Syateki_Wf",
  [0x142]="Obj_Skateblock",
  [0x143]="Obj_Iceblock",
  [0x144]="En_Bigpamet",
  [0x145]="En_Syateki_Dekunuts",
  [0x146]="Elf_Msg3",
  [0x147]="En_Fg",
  [0x148]="Dm_Ravine",
  [0x149]="Dm_Sa",
  [0x14A]="En_Slime",
  [0x14B]="En_Pr",
  [0x14C]="Obj_Toudai",
  [0x14D]="Obj_Entotu",
  [0x14E]="Obj_Bell",
  [0x14F]="En_Syateki_Okuta",
  [0x151]="Obj_Shutter",
  [0x152]="Dm_Zl",
  [0x153]="En_Elfgrp",
  [0x154]="Dm_Tsg",
  [0x155]="En_Baguo",
  [0x156]="Obj_Vspinyroll",
  [0x157]="Obj_Smork",
  [0x158]="En_Test2",
  [0x159]="En_Test3",
  [0x15A]="En_Test4",
  [0x15B]="En_Bat",
  [0x15C]="En_Sekihi",
  [0x15D]="En_Wiz",
  [0x15E]="En_Wiz_Brock",
  [0x15F]="En_Wiz_Fire",
  [0x160]="Eff_Change",
  [0x161]="Dm_Statue",
  [0x162]="Obj_Fireshield",
  [0x163]="Bg_Ladder",
  [0x164]="En_Mkk",
  [0x165]="Demo_Getitem",
  [0x167]="En_Dnb",
  [0x168]="En_Dnh",
  [0x169]="En_Dnk",
  [0x16A]="En_Dnq",
  [0x16C]="Bg_Keikoku_Saku",
  [0x16D]="Obj_Hugebombiwa",
  [0x16E]="En_Firefly2",
  [0x16F]="En_Rat",
  [0x170]="En_Water_Effect",
  [0x171]="En_Kusa2",
  [0x172]="Bg_Spout_Fire",
  [0x174]="Bg_Dblue_Movebg",
  [0x175]="En_Dy_Extra",
  [0x176]="En_Bal",
  [0x177]="En_Ginko_Man",
  [0x178]="En_Warp_Uzu",
  [0x179]="Obj_Driftice",
  [0x17A]="En_Look_Nuts",
  [0x17B]="En_Mushi2",
  [0x17C]="En_Fall",
  [0x17D]="En_Mm3",
  [0x17E]="Bg_Crace_Movebg",
  [0x17F]="En_Dno",
  [0x180]="En_Pr2",
  [0x181]="En_Prz",
  [0x182]="En_Jso2",
  [0x183]="Obj_Etcetera",
  [0x184]="En_Egol",
  [0x185]="Obj_Mine",
  [0x186]="Obj_Purify",
  [0x187]="En_Tru",
  [0x188]="En_Trt",
  [0x18B]="En_Test5",
  [0x18C]="En_Test6",
  [0x18D]="En_Az",
  [0x18E]="En_Estone",
  [0x18F]="Bg_Hakugin_Post",
  [0x190]="Dm_Opstage",
  [0x191]="Dm_Stk",
  [0x192]="Dm_Char00",
  [0x193]="Dm_Char01",
  [0x194]="Dm_Char02",
  [0x195]="Dm_Char03",
  [0x196]="Dm_Char04",
  [0x197]="Dm_Char05",
  [0x198]="Dm_Char06",
  [0x199]="Dm_Char07",
  [0x19A]="Dm_Char08",
  [0x19B]="Dm_Char09",
  [0x19C]="Obj_Tokeidai",
  [0x19E]="En_Mnk",
  [0x19F]="En_Egblock",
  [0x1A0]="En_Guard_Nuts",
  [0x1A1]="Bg_Hakugin_Bombwall",
  [0x1A2]="Obj_Tokei_Tobira",
  [0x1A3]="Bg_Hakugin_Elvpole",
  [0x1A4]="En_Ma4",
  [0x1A5]="En_Twig",
  [0x1A6]="En_Po_Fusen",
  [0x1A7]="En_Door_Etc",
  [0x1A8]="En_Bigokuta",
  [0x1A9]="Bg_Icefloe",
  [0x1AA]="Obj_Ocarinalift",
  [0x1AB]="En_Time_Tag",
  [0x1AC]="Bg_Open_Shutter",
  [0x1AD]="Bg_Open_Spot",
  [0x1AE]="Bg_Fu_Kaiten",
  [0x1AF]="Obj_Aqua",
  [0x1B0]="En_Elforg",
  [0x1B1]="En_Elfbub",
  [0x1B3]="En_Fu_Mato",
  [0x1B4]="En_Fu_Kago",
  [0x1B5]="En_Osn",
  [0x1B6]="Bg_Ctower_Gear",
  [0x1B7]="En_Trt2",
  [0x1B8]="Obj_Tokei_Step",
  [0x1B9]="Bg_Lotus",
  [0x1BA]="En_Kame",
  [0x1BB]="Obj_Takaraya_Wall",
  [0x1BC]="Bg_Fu_Mizu",
  [0x1BD]="En_Sellnuts",
  [0x1BE]="Bg_Dkjail_Ivy",
  [0x1C0]="Obj_Visiblock",
  [0x1C1]="En_Takaraya",
  [0x1C2]="En_Tsn",
  [0x1C3]="En_Ds2n",
  [0x1C4]="En_Fsn",
  [0x1C5]="En_Shn",
  [0x1C7]="En_Stop_heishi",
  [0x1C8]="Obj_Bigicicle",
  [0x1C9]="En_Lift_Nuts",
  [0x1CA]="En_Tk",
  [0x1CC]="Bg_Market_Step",
  [0x1CD]="Obj_Lupygamelift",
  [0x1CE]="En_Test7",
  [0x1CF]="Obj_Lightblock",
  [0x1D0]="Mir_Ray2",
  [0x1D1]="En_Wdhand",
  [0x1D2]="En_Gamelupy",
  [0x1D3]="Bg_Danpei_Movebg",
  [0x1D4]="En_Snowwd",
  [0x1D5]="En_Pm",
  [0x1D6]="En_Gakufu",
  [0x1D7]="Elf_Msg4",
  [0x1D8]="Elf_Msg5",
  [0x1D9]="En_Col_Man",
  [0x1DA]="En_Talk_Gibud",
  [0x1DB]="En_Giant",
  [0x1DC]="Obj_Snowball",
  [0x1DD]="Boss_Hakugin",
  [0x1DE]="En_Gb2",
  [0x1DF]="En_Onpuman",
  [0x1E0]="Bg_Tobira01",
  [0x1E1]="En_Tag_Obj",
  [0x1E2]="Obj_Dhouse",
  [0x1E3]="Obj_Hakaisi",
  [0x1E4]="Bg_Hakugin_Switch",
  [0x1E6]="En_Snowman",
  [0x1E7]="TG_Sw",
  [0x1E8]="En_Po_Sisters",
  [0x1E9]="En_Pp",
  [0x1EA]="En_Hakurock",
  [0x1EB]="En_Hanabi",
  [0x1EC]="Obj_Dowsing",
  [0x1ED]="Obj_Wind",
  [0x1EE]="En_Racedog",
  [0x1EF]="En_Kendo_Js",
  [0x1F0]="Bg_Botihasira",
  [0x1F1]="En_Fish2",
  [0x1F2]="En_Pst",
  [0x1F3]="En_Poh",
  [0x1F4]="Obj_Spidertent",
  [0x1F5]="En_Zoraegg",
  [0x1F6]="En_Kbt",
  [0x1F7]="En_Gg",
  [0x1F8]="En_Maruta",
  [0x1F9]="Obj_Snowball2",
  [0x1FA]="En_Gg2",
  [0x1FB]="Obj_Ghaka",
  [0x1FC]="En_Dnp",
  [0x1FD]="En_Dai",
  [0x1FE]="Bg_Goron_Oyu",
  [0x1FF]="En_Kgy",
  [0x200]="En_Invadepoh",
  [0x201]="En_Gk",
  [0x202]="En_An",
  [0x204]="En_Bee",
  [0x205]="En_Ot",
  [0x206]="En_Dragon",
  [0x207]="Obj_Dora",
  [0x208]="En_Bigpo",
  [0x209]="Obj_Kendo_Kanban",
  [0x20A]="Obj_Hariko",
  [0x20B]="En_Sth",
  [0x20C]="Bg_Sinkai_Kabe",
  [0x20D]="Bg_Haka_Curtain",
  [0x20E]="Bg_Kin2_Bombwall",
  [0x20F]="Bg_Kin2_Fence",
  [0x210]="Bg_Kin2_Picture",
  [0x211]="Bg_Kin2_Shelf",
  [0x212]="En_Rail_Skb",
  [0x213]="En_Jg",
  [0x214]="En_Tru_Mt",
  [0x215]="Obj_Um",
  [0x216]="En_Neo_Reeba",
  [0x217]="Bg_Mbar_Chair",
  [0x218]="Bg_Ikana_Block",
  [0x219]="Bg_Ikana_Mirror",
  [0x21A]="Bg_Ikana_Rotaryroom",
  [0x21B]="Bg_Dblue_Balance",
  [0x21C]="Bg_Dblue_Waterfall",
  [0x21D]="En_Kaizoku",
  [0x21E]="En_Ge2",
  [0x21F]="En_Ma_Yts",
  [0x220]="En_Ma_Yto",
  [0x221]="Obj_Tokei_Turret",
  [0x222]="Bg_Dblue_Elevator",
  [0x223]="Obj_Warpstone",
  [0x224]="En_Zog",
  [0x225]="Obj_Rotlift",
  [0x226]="Obj_Jg_Gakki",
  [0x227]="Bg_Inibs_Movebg",
  [0x228]="En_Zot",
  [0x229]="Obj_Tree",
  [0x22A]="Obj_Y2lift",
  [0x22B]="Obj_Y2shutter",
  [0x22C]="Obj_Boat",
  [0x22D]="Obj_Taru",
  [0x22E]="Obj_Hunsui",
  [0x22F]="En_Jc_Mato",
  [0x230]="Mir_Ray3",
  [0x231]="En_Zob",
  [0x232]="Elf_Msg6",
  [0x233]="Obj_Nozoki",
  [0x234]="En_Toto",
  [0x235]="En_Railgibud",
  [0x236]="En_Baba",
  [0x237]="En_Suttari",
  [0x238]="En_Zod",
  [0x239]="En_Kujiya",
  [0x23A]="En_Geg",
  [0x23B]="Obj_Kinoko",
  [0x23C]="Obj_Yasi",
  [0x23D]="En_Tanron1",
  [0x23E]="En_Tanron2",
  [0x23F]="En_Tanron3",
  [0x240]="Obj_Chan",
  [0x241]="En_Zos",
  [0x242]="En_S_Goro",
  [0x243]="En_Nb",
  [0x244]="En_Ja",
  [0x245]="Bg_F40_Block",
  [0x246]="Bg_F40_Switch",
  [0x247]="En_Po_Composer",
  [0x248]="En_Guruguru",
  [0x249]="Oceff_Wipe5",
  [0x24A]="En_Stone_heishi",
  [0x24B]="Oceff_Wipe6",
  [0x24C]="En_Scopenuts",
  [0x24D]="En_Scopecrow",
  [0x24E]="Oceff_Wipe7",
  [0x24F]="Eff_Kamejima_Wave",
  [0x250]="En_Hg",
  [0x251]="En_Hgo",
  [0x252]="En_Zov",
  [0x253]="En_Ah",
  [0x254]="Obj_Hgdoor",
  [0x255]="Bg_Ikana_Bombwall",
  [0x256]="Bg_Ikana_Ray",
  [0x257]="Bg_Ikana_Shutter",
  [0x258]="Bg_Haka_Bombwall",
  [0x259]="Bg_Haka_Tomb",
  [0x25A]="En_Sc_Ruppe",
  [0x25B]="Bg_Iknv_Doukutu",
  [0x25C]="Bg_Iknv_Obj",
  [0x25D]="En_Pamera",
  [0x25E]="Obj_HsStump",
  [0x25F]="En_Hidden_Nuts",
  [0x260]="En_Zow",
  [0x261]="En_Talk",
  [0x262]="En_Al",
  [0x263]="En_Tab",
  [0x264]="En_Nimotsu",
  [0x265]="En_Hit_Tag",
  [0x266]="En_Ruppecrow",
  [0x267]="En_Tanron4",
  [0x268]="En_Tanron5",
  [0x269]="En_Tanron6",
  [0x26A]="En_Daiku2",
  [0x26B]="En_Muto",
  [0x26C]="En_Baisen",
  [0x26D]="En_Heishi",
  [0x26E]="En_Demo_heishi",
  [0x26F]="En_Dt",
  [0x270]="En_Cha",
  [0x271]="Obj_Dinner",
  [0x272]="Eff_Lastday",
  [0x273]="Bg_Ikana_Dharma",
  [0x274]="En_Akindonuts",
  [0x275]="Eff_Stk",
  [0x276]="En_Ig",
  [0x277]="En_Rg",
  [0x278]="En_Osk",
  [0x279]="En_Sth2",
  [0x27A]="En_Yb",
  [0x27B]="En_Rz",
  [0x27C]="En_Scopecoin",
  [0x27D]="En_Bjt",
  [0x27E]="En_Bomjima",
  [0x27F]="En_Bomjimb",
  [0x280]="En_Bombers",
  [0x281]="En_Bombers2",
  [0x282]="En_Bombal",
  [0x283]="Obj_Moon_Stone",
  [0x284]="Obj_Mu_Pict",
  [0x285]="Bg_Ikninside",
  [0x286]="Eff_Zoraband",
  [0x287]="Obj_Kepn_Koya",
  [0x288]="Obj_Usiyane",
  [0x289]="En_Nnh",
  [0x28A]="Obj_Kzsaku",
  [0x28B]="Obj_Milk_Bin",
  [0x28C]="En_Kitan",
  [0x28D]="Bg_Astr_Bombwall",
  [0x28E]="Bg_Iknin_Susceil",
  [0x28F]="En_Bsb",
  [0x290]="En_Recepgirl",
  [0x291]="En_Thiefbird",
  [0x292]="En_Jgame_Tsn",
  [0x293]="Obj_Jgame_Light",
  [0x294]="Obj_Yado",
  [0x295]="Demo_Syoten",
  [0x296]="Demo_Moonend",
  [0x297]="Bg_Lbfshot",
  [0x298]="Bg_Last_Bwall",
  [0x299]="En_And",
  [0x29A]="En_Invadepoh_Demo",
  [0x29B]="Obj_Danpeilift",
  [0x29C]="En_Fall2",
  [0x29D]="Dm_Al",
  [0x29E]="Dm_An",
  [0x29F]="Dm_Ah",
  [0x2A0]="Dm_Nb",
  [0x2A1]="En_Drs",
  [0x2A2]="En_Ending_Hero",
  [0x2A3]="Dm_Bal",
  [0x2A4]="En_Paper",
  [0x2A5]="En_Hint_Skb",
  [0x2A6]="Dm_Tag",
  [0x2A7]="En_Bh",
  [0x2A8]="En_Ending_Hero2",
  [0x2A9]="En_Ending_Hero3",
  [0x2AA]="En_Ending_Hero4",
  [0x2AB]="En_Ending_Hero5",
  [0x2AC]="En_Ending_Hero6",
  [0x2AD]="Dm_Gm",
  [0x2AE]="Obj_Swprize",
  [0x2AF]="En_Invisible_Ruppe",
  [0x2B0]="Obj_Ending",
  [0x2B1]="En_Rsn",
}

local function u8(a)  return memory.read_u8(a, DOMAIN) end
local function u16(a) return memory.read_u16_be(a, DOMAIN) end
local function s16(a) return memory.read_s16_be(a, DOMAIN) end
local function u32(a) return memory.read_u32_be(a, DOMAIN) end
local function f32(a) return memory.readfloat(a, true, DOMAIN) end
local function phys(p) return p % 0x800000 end   -- 0x80xxxxxx -> RDRAM offset

local function is_node(a)
  return a >= 0 and a < 0x800000 - NODE_SIZE and u16(a) == 0x7373 and u16(a + 2) <= 1
end

-- Walk a chain from `head`; returns list of node offsets and whether it ended cleanly.
local function walk(head)
  local list, cur = {}, head
  while true do
    list[#list + 1] = cur
    local nxt = u32(cur + 8)
    if nxt == 0 then return list, true end
    nxt = phys(nxt)
    if not is_node(nxt) or phys(u32(nxt + 0xC)) ~= cur or #list > 4000 then return list, false end
    cur = nxt
  end
end

local function actor_at(node)
  if u16(node + 2) ~= 0 or u32(node + 4) < 0x144 then return nil end
  local d = node + NODE_SIZE
  local id, cat = s16(d), u8(d + 2)
  local upd = u32(d + 0x138)
  if id == 0 and cat ~= 2 then return nil end
  if ACTOR_NAMES[id] and cat < 12 and (upd == 0 or (upd >= 0x80000000 and upd < 0x80800000)) then
    return id, cat
  end
  return nil
end

-- Scan RAM for chain heads (prev == NULL); pick the arena containing the Player actor.
local function find_zelda_arena()
  local best
  for base = SCAN_START, SCAN_END - 1, 0x10000 do
    local b = memory.read_bytes_as_array(base, 0x10000, DOMAIN)
    local o = (b[0] ~= nil) and 0 or 1   -- tolerate 0- or 1-indexed tables
    for i = 0, 0x10000 - 0x10, 0x10 do
      if b[i+o] == 0x73 and b[i+o+1] == 0x73 and b[i+o+2] == 0 and b[i+o+3] <= 1
         and b[i+o+12] == 0 and b[i+o+13] == 0 and b[i+o+14] == 0 and b[i+o+15] == 0 then
        local head = base + i
        local list = walk(head)
        if #list > 3 then
          for _, n in ipairs(list) do
            local id, cat = actor_at(n)
            if id == 0 and cat == 2 then return head end
          end
          if not best or #list > #walk(best) then best = head end
        end
      end
    end
  end
  return best
end

local head, last_scan = nil, -1000
local form = forms.newform(560, 720, "MM heap viewer")
local box = forms.textbox(form, "", 540, 640, nil, 5, 35, true, true, "Vertical")
forms.button(form, "Rescan heap", function() head = nil; last_scan = -1000 end, 5, 5, 100, 25)
local only_used = false
forms.button(form, "Toggle free/used", function() only_used = not only_used end, 110, 5, 120, 25)
event.onexit(function() forms.destroy(form) end)

local function hex(v, w) return string.format("%0" .. (w or 8) .. "X", v) end

while true do
  local fc = emu.framecount()
  if (not head or not is_node(head) or u32(head + 0xC) ~= 0) and fc - last_scan > 30 then
    head = find_zelda_arena(); last_scan = fc
  end

  local player, test4_ovl, test4_patch
  if head then
    local list, clean = walk(head)
    local lab, nodes_set = {}, {}
    for _, n in ipairs(list) do nodes_set[#nodes_set + 1] = n end
    for _, n in ipairs(list) do
      local id, cat = actor_at(n)
      if id then
        local d = n + NODE_SIZE
        lab[n] = string.format("%s (id %03X cat %d)", ACTOR_NAMES[id], id, cat)
        if id == 0 and cat == 2 then player = d end
        for _, off in ipairs({0x138, 0x130, 0x13C}) do
          local fp = phys(u32(d + off))
          for _, b in ipairs(nodes_set) do
            if not lab[b] and fp >= b + NODE_SIZE and fp < b + NODE_SIZE + u32(b + 4) then
              lab[b] = "ovl_" .. ACTOR_NAMES[id] .. " (code)"
              if id == 0x15A then test4_ovl = b end
              break
            end
          end
        end
      end
    end

    if test4_ovl then   -- find "ori ?, zero, 0xFFF1" (the credits-warp patch target)
      local d, sz = test4_ovl + NODE_SIZE, u32(test4_ovl + 4)
      for o = 0, sz - 4, 4 do
        if u16(d + o + 2) == 0xFFF1 then test4_patch = 0x80000000 + d + o + 3; break end
      end
    end

    if fc % REFRESH == 0 then
      local out = { string.format("Zelda arena head %s  nodes %d%s  (node size %X)",
        hex(0x80000000 + head), #list, clean and "" or "  ** CHAIN BROKEN **", NODE_SIZE) }
      if test4_patch then out[#out + 1] = "En_Test4 FFF1 low byte (credits patch): " .. hex(test4_patch) end
      out[#out + 1] = "node      data      state size    contents"
      for _, n in ipairs(list) do
        local free = u16(n + 2) ~= 0
        if not (only_used and free) then
          out[#out + 1] = string.format("%s  %s  %s  %s  %s", hex(0x80000000 + n),
            hex(0x80000000 + n + NODE_SIZE), free and "FREE" or "used", hex(u32(n + 4), 6), lab[n] or "")
        end
      end
      forms.settext(box, table.concat(out, "\r\n"))
    end
  end

  if player then
    local p = player
    gui.text(10, 40, string.format("Link shape.rot.y  %04X", u16(p + 0xBE)))
    gui.text(10, 55, string.format("Link world.rot.y  %04X", u16(p + 0x32)))
    gui.text(10, 70, string.format("Player yaw(+AD4)  %04X", u16(p + 0xAD4)))
    gui.text(10, 85, string.format("pos %.3f %.3f %.3f", f32(p + 0x24), f32(p + 0x28), f32(p + 0x2C)))
    gui.text(10, 100, "Link @ " .. hex(0x80000000 + p))
  else
    gui.text(10, 40, "Player actor not found (rescan / not in gameplay)")
  end
  emu.frameadvance()
end
