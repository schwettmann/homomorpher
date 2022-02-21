import * as d3 from 'd3';
import {makeUrl, toPayload} from '../etc/apiHelpers'
import {URLHandler} from '../etc/URLHandler';


const baseurl = URLHandler.basicURL()

export interface TransformRequest {
    category: number,
    zs: number[][],
    transformID: string
}

export type Base64Image = string;

export interface TransitionMeta {
    id: string,
    descr: string,
    type: 'original' | 'OWN',
    file?: string,
    utc_created?: string
}

export interface TransformResponse {
    request: TransformRequest,
    res: {
        in: Base64Image,
        out: Base64Image
    }

}

export class API {

    constructor(private baseURL: string = null) {
        if (this.baseURL == null) {
            this.baseURL = baseurl + '/api';
        }
    }

    all_transitions(): Promise<TransitionMeta[]> {
        const url = makeUrl(this.baseURL + "/all_transitions", {})
        return d3.json(url)
    }

    /**
     * return a random vector of valid size for GAN
     * @param seed - seed for random generator (disfunct)
     * @return array of vectors -- currently only one vector
     */
    random_z(seed: number = 100): Promise<number[][]> {
        const url = makeUrl(this.baseURL + "/random_z", {seed})
        return d3.json(url)
    }


    random_images(count: number, category: number): Promise<{ z: number[], image: string }[]> {
        const url = makeUrl(this.baseURL + "/random_images", {count, category})
        return d3.json(url)
    }

    learn(from_zs: number[][], to_zs: number[][], descr = null): Promise<{ request: {}, result: TransitionMeta }> {
        const toSend = {
            from_zs, to_zs
        }
        if (descr) toSend["descr"] = descr;

        const url = makeUrl(this.baseURL + '/learn');
        const payload = toPayload(toSend)

        return d3.json(url, payload)
    }


    /**
     * all mappings of categories to categoryIDs
     */
    all_categories(): Promise<[string, number][]> {
        const url = makeUrl(this.baseURL + "/categories", {})
        return d3.json(url)
    }

    transformImg(category: number, z: number[], transformID: string): Promise<TransformResponse> {
        const toSend: TransformRequest = {
            category, zs: [z], transformID
        }

        const url = makeUrl(this.baseURL + '/transform');
        const payload = toPayload(toSend)

        console.log("--- POST " + url, payload);

        return d3.json(url, payload)
    }


    /**
     * Example API call, typed with expected response
     *
     * @param firstname
     */
    getAHi(firstname: string): Promise<string> {
        const toSend = {
            firstname: firstname
        }

        const url = makeUrl(this.baseURL + "/get-a-hi", toSend)
        console.log("--- GET " + url);

        return d3.json(url)
    }

    /**
     * Example POST request, typed with expected response
     *
     * @param firstname
     */
    postABye(firstname: string): Promise<string> {
        const toSend = {
            firstname: firstname,
        }

        const url = makeUrl(this.baseURL + '/post-a-bye');
        const payload = toPayload(toSend)

        console.log("--- POST " + url, payload);

        return d3.json(url, payload)
    }

};
