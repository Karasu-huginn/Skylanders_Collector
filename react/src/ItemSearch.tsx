import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ItemCard } from "./components/ItemCard";
import type { ItemsListResponse } from "./types";

export function ItemSearch() {
    const [search, setSearch] = useState("");
    const [page, setPage] = useState(1);
    const [isCaptured, setIsCaptured] = useState(false);
    const [isUncaptured, setIsUncaptured] = useState(false);
    const [isDuplicate, setIsDuplicate] = useState(false);
    const { isLoading, isError, error, data, refetch } = useQuery<ItemsListResponse>({
        queryKey: ['item_search', search, page, isCaptured, isUncaptured, isDuplicate],
        queryFn: async () => {
            const res = await fetch(`/api/items?search=${search}&page=${page}&is_captured=${isCaptured}&is_uncaptured=${isUncaptured}&is_duplicate=${isDuplicate}`);
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
        },
        staleTime: 1000 * 60 * 5,
    });

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        refetch();
    }

    const changePage = (page_add: number) => {
        setPage(page + page_add);
        refetch();
    }

    const filterCount = (state_captured: boolean, state_uncaptured: boolean, state_duplicate: boolean) => {
        setIsCaptured(state_captured);
        setIsUncaptured(state_uncaptured);
        setIsDuplicate(state_duplicate);
        setPage(1);
    }

    return <>
        <form onSubmit={handleSearch} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <span>
                <label htmlFor="search">Nom de la figurine : </label>
                <input id="search" name="search" type="text" placeholder="Nom de la figurine..." value={search} onChange={(e) => setSearch(e.target.value)} />
            </span>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <span>
                    <input type="checkbox" name="is_captured" checked={isCaptured} onChange={() => filterCount(!isCaptured, false, false)} />
                    <label htmlFor="search">Capturés</label>
                </span>
                <span>
                    <input type="checkbox" name="is_uncaptured" checked={isUncaptured} onChange={() => filterCount(false, !isUncaptured, false)} />
                    <label htmlFor="search">À capturer</label>
                </span>
                <span>
                    <input type="checkbox" name="is_duplicate" checked={isDuplicate} onChange={() => filterCount(false, false, !isDuplicate)} />
                    <label htmlFor="search">Doublons</label>
                </span>
            </div>
            <button type="submit">Rechercher</button>
        </form>

        {isLoading && <div>Chargement...</div>}
        {isError && <div>Erreur : {(error as Error).message}</div>}
        {data && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "1rem" }}>
                {data.items.length > 0 ? (
                    data.items.map((result) => (
                        <ItemCard key={result.id} item={result} />
                    ))
                ) : (
                    <h3>Aucun résultat trouvé. Essayez d'ajuster vos critères de recherche.</h3>
                )}
            </div>
        )}
        {page > 1 && <button onClick={() => changePage(-1)}>Page Précédente</button>}
        {data && data.items.length == 10 && <button onClick={() => changePage(1)}>Page Suivante</button>}
    </>
}
