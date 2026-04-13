export type ItemType =
    | "Skylander"
    | "Giant"
    | "Traptanium Crystal Trap"
    | "Swapper"
    | "Vehicle"
    | "Sensei"
    | "Villain Sensei"

export interface EditionResponse {
    id: number;
    name: string;
    release_date: string;
}

export interface ElementResponse {
    id: number;
    name: string;
}

export interface TypeResponse {
    id: number;
    name: string;
}

export interface VariantResponse {
    id: number;
    name: string;
}

export interface Item {
    id: number;
    name: string;
    details?: string;
    type: TypeResponse;
    edition: EditionResponse;
    image?: string;
    count: number;
    price: number;
    variant: VariantResponse;
    element: ElementResponse | null;
    swapper: boolean;
    bot_count?: number;
    top_count?: number;
}

export interface ItemsListResponse {
    items: Item[];
}
