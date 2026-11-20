import { createCinematic, CineData } from "./Cinematic";
import data from "./kelebihan.json";

// v5: iklan profesional "5 kelebihan Gran Max" (Pick Up bak tinggi angkut sawit), efek dikunci ke lagu.
export const GranMaxKelebihan = createCinematic(data as unknown as CineData, { dir: "kelebihan", depthBlur: false, look: "warm" });
