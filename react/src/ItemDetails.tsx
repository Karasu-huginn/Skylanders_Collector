import type { Item } from "./ItemSearch";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";

export function ItemDetails() {
    const { item_id } = useParams();
    const { isLoading, isError, error, data } = useQuery<Item>({
        queryKey: ['item_details', item_id],
        //? get ip from external file ?
        queryFn: async () => {
            const res = await fetch(`http://127.0.0.1:8000/items/${item_id}`, {
                mode: "cors"
            });
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
        }
    });

    return <>
        <div style={{ display: "flex", flexDirection: "column" }}>
            {isLoading && <div>Chargement...</div>}
            {isError && <div>Erreur : {(error as Error).message}</div>}
            <h1>{data?.name}</h1>
            <h2>{data?.id}</h2>
            <h2>{data?.type}</h2>
            <h2>{data?.element}</h2>
            <h2>{data?.variant}</h2>
            <h2>{data?.count}</h2>
        </div>
    </>
}