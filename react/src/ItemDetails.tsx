import type { Item } from "./types";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";

export function ItemDetails() {
    const { item_id } = useParams();
    const { isLoading, isError, error, data } = useQuery<Item>({
        queryKey: ['item_details', item_id],
        queryFn: async () => {
            const res = await fetch(`/api/items/${item_id}`);
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
            <h2>{data?.type.name}</h2>
            <h2>{data?.element.name}</h2>
            <h2>{data?.variant.name}</h2>
            <h2>{data?.count}</h2>
        </div>
    </>
}
