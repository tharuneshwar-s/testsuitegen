/**
 * Intents: HAPPY_PATH, OBJECT_MISSING_FIELD, TYPE_VIOLATION
 * 
 * Order Processor Module
 * Demonstrates structural handling of complex nested objects.
 */

export interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
  discount?: number;
}

export interface Address {
    street: string;
    city: string;
    zipCode: string;
}

export interface Order {
  id: string;
  customer: {
      name: string;
      email: string;
      address?: Address;
  };
  items: OrderItem[];
  status: "pending" | "shipped" | "delivered";
}

export function calculateTotal(order: Order): number {
  if (!order.items || !Array.isArray(order.items)) {
    throw new Error("Invalid order: items missing");
  }

  return order.items.reduce((total, item) => {
    // Malformed item check
    if (typeof item.price !== "number" || typeof item.quantity !== "number") {
      throw new Error(`Invalid item in order ${order.id}`);
    }
    const itemTotal = item.price * item.quantity;
    const discount = item.discount || 0;
    return total + Math.max(0, itemTotal - discount);
  }, 0);
}

export function getShippingLabel(order: Order): string {
    // Structural check: optional address
    if (!order.customer.address) {
        throw new Error("Shipping address missing");
    }
    const { street, city, zipCode } = order.customer.address;
    return `${order.customer.name}\n${street}\n${city}, ${zipCode}`;
}
