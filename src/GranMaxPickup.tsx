import { createCinematic, CineData } from "./Cinematic";
import data from "./pickup.json";

// v6: iklan profesional "dari showroom sampai kebun" dari 4 klip, 30 fps, efek dikunci ke lagu.
export const GranMaxPickup = createCinematic(data as unknown as CineData, { dir: "pickup", depthBlur: false, look: "clean" });
