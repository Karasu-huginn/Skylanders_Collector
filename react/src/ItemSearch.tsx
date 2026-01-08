import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ItemCard } from "./ItemCard";

export interface Item {
    id: number,
    name: string,
    details?: string,
    type: number, //todo change from id to name, requires join in sql request
    edition: number, //todo change from id to name, requires join in sql request
    image?: string,
    count: number,
    price: number, //* price in cents
    variant: number, //todo change from id to name, requires join in sql request
    element: number, //todo change from id to name, requires join in sql request
    swapper: boolean,
    bot_count?: number,
    top_count?: number,
}

interface ItemsListResponse {
    items: Item[],
    length: number,
}

export function ItemSearch() {
    const [search, setSearch] = useState("");
    const { isLoading, isError, error, data, refetch } = useQuery<ItemsListResponse>({
        queryKey: ['item_search', search],
        //? get ip from external file ?
        queryFn: async () => {
            const res = await fetch(`http://127.0.0.1:8000/items?search=${search}`, {
                mode: "cors"
            });
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
        },
        enabled: false,
        staleTime: 1000 * 60 * 5,
    });

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        refetch();
    }

    console.log(data);

    return <>
        <form onSubmit={handleSearch} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <span>
                <label htmlFor="search">Nom de la figurine : </label>
                <input id="search" name="search" type="text" placeholder="Nom de la figurine..." value={search} onChange={(e) => setSearch(e.target.value)} />
            </span>
            <button type="submit">Rechercher</button>
        </form>

        {isLoading && <div>Chargement...</div>}
        {isError && <div>Erreur : {(error as Error).message}</div>}
        {data && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
                {data.items.length > 0 ? (
                    data.items.map((result) => (
                        <ItemCard item={result} />
                    ))
                ) : (
                    <h3>Aucun résultat trouvé. Essayez d'ajuster vos critères de recherche.</h3>
                )}
            </div>
        )}
    </>
}