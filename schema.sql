global_inventory: 
create table
  public.global_inventory (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    num_red_ml integer null,
    gold integer null,
    num_blue_ml integer null,
    num_green_ml integer null,
    num_dark_ml integer null default 0,
    total_potions bigint null,
    constraint global_inventory_pkey primary key (id)
  ) tablespace pg_default;


  potions_inventory:
  create table
  public.potions_inventory (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    quantity integer null,
    price integer null,
    sku text null,
    name text null,
    type integer[] null,
    constraint potions_inventory_pkey primary key (id)
  ) tablespace pg_default;

  carts:
  create table
  public.carts (
    cart_id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    customer_name text null,
    constraint carts_pkey primary key (cart_id)
  ) tablespace pg_default;

  cart_items:
  create table
  public.cart_items (
    cart_id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    id bigint not null,
    quantity bigint not null,
    constraint cart_items_pkey primary key (cart_id),
    constraint cart_items_id_fkey foreign key (id) references potions_inventory (id)
  ) tablespace pg_default;