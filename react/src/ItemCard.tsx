import { Link } from "react-router";
import type { Item } from "./ItemSearch";

interface itemProps {
    item: Item;
}

export function ItemCard(props: itemProps) {
    const { item } = props;
    return <>
        <div style={{ display: "flex", flexDirection: "column" }}>
            <h1>{item.name}</h1>
            <h2>{item.element}</h2>
            <h2>{item.image}</h2>
            <Link to={`/item/${item.id}`}>Voir plus</Link>
        </div>
    </>
}