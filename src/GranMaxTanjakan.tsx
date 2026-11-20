import { createCinematic, CineData } from "./Cinematic";
import data from "./tanjakan.json";

// v4: cinematic TikTok, Gran Max angkut 2.900 kg sawit di tanjakan. Potongan dikunci ke hentakan lagu.
export const GranMaxTanjakan = createCinematic(data as unknown as CineData, { dir: "tanjakan" });
