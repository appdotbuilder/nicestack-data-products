from nicegui import ui
from datetime import datetime, date
import logging
from app.data_product_service import (
    get_all_data_products,
    create_data_product,
    update_data_product,
    delete_data_product,
    get_data_product_by_id,
)
from app.models import DataProductCreate, DataProductUpdate


logger = logging.getLogger(__name__)


def apply_modern_theme():
    """Apply modern color theme for the application."""
    ui.colors(
        primary="#2563eb",  # Professional blue
        secondary="#64748b",  # Subtle gray
        accent="#10b981",  # Success green
        positive="#10b981",
        negative="#ef4444",  # Error red
        warning="#f59e0b",  # Warning amber
        info="#3b82f6",  # Info blue
    )


class TextStyles:
    """Reusable text styles for consistent typography."""

    HEADING = "text-2xl font-bold text-gray-800 mb-4"
    SUBHEADING = "text-lg font-semibold text-gray-700 mb-2"
    BODY = "text-base text-gray-600 leading-relaxed"
    CAPTION = "text-sm text-gray-500"


def create():
    """Create the data products module."""
    apply_modern_theme()

    @ui.page("/data-products")
    def data_products_page():
        """Main data products page with table view and CRUD operations."""

        # Page header
        with ui.card().classes("w-full p-6 mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-0 shadow-lg"):
            ui.label("Data Products Dashboard").classes("text-3xl font-bold text-gray-800 mb-2")
            ui.label("Unity Catalog schemas and their metadata").classes(TextStyles.BODY)

        # Main content container
        with ui.card().classes("w-full p-6 shadow-lg rounded-xl bg-white"):
            # Action buttons row
            with ui.row().classes("w-full justify-between items-center mb-6"):
                ui.label("Data Products").classes(TextStyles.SUBHEADING + " mb-0")

                with ui.row().classes("gap-2"):
                    refresh_btn = ui.button("Refresh", icon="refresh", on_click=lambda: refresh_table())
                    refresh_btn.classes("bg-gray-100 text-gray-700 hover:bg-gray-200")

                    add_btn = ui.button("Add Data Product", icon="add", on_click=lambda: show_add_dialog())
                    add_btn.classes("bg-primary text-white hover:bg-blue-600")

            # Data products table
            table_container = ui.column().classes("w-full")

            # Stats row
            stats_container = ui.row().classes("w-full gap-4 mb-6")

            def refresh_table():
                """Refresh the data products table."""
                try:
                    data_products = get_all_data_products()

                    # Update stats
                    stats_container.clear()
                    with stats_container:
                        # Total count card
                        with ui.card().classes("p-4 bg-blue-50 border-l-4 border-blue-500 flex-1"):
                            with ui.column().classes("gap-1"):
                                ui.label("Total Data Products").classes("text-sm text-blue-600 font-medium")
                                ui.label(str(len(data_products))).classes("text-2xl font-bold text-blue-800")

                        # Recent additions card (last 7 days)
                        from datetime import datetime, timedelta

                        recent_count = sum(
                            1
                            for dp in data_products
                            if dp.creation_date and dp.creation_date > datetime.utcnow() - timedelta(days=7)
                        )
                        with ui.card().classes("p-4 bg-green-50 border-l-4 border-green-500 flex-1"):
                            with ui.column().classes("gap-1"):
                                ui.label("Recent (7 days)").classes("text-sm text-green-600 font-medium")
                                ui.label(str(recent_count)).classes("text-2xl font-bold text-green-800")

                        # Unique owners card
                        unique_owners = len(set(dp.owner for dp in data_products))
                        with ui.card().classes("p-4 bg-purple-50 border-l-4 border-purple-500 flex-1"):
                            with ui.column().classes("gap-1"):
                                ui.label("Unique Owners").classes("text-sm text-purple-600 font-medium")
                                ui.label(str(unique_owners)).classes("text-2xl font-bold text-purple-800")

                    table_container.clear()

                    with table_container:
                        if not data_products:
                            with ui.card().classes("p-8 text-center bg-gray-50 border-dashed border-2 border-gray-300"):
                                ui.icon("inbox", size="3rem").classes("text-gray-400 mb-4")
                                ui.label("No data products found").classes("text-xl text-gray-600 mb-2")
                                ui.label('Click "Add Data Product" to create your first one').classes(
                                    TextStyles.CAPTION
                                )
                        else:
                            # Create table with data
                            columns = [
                                {
                                    "name": "schema_name",
                                    "label": "Schema Name",
                                    "field": "schema_name",
                                    "required": True,
                                    "align": "left",
                                    "sortable": True,
                                },
                                {
                                    "name": "description",
                                    "label": "Description",
                                    "field": "description",
                                    "align": "left",
                                    "sortable": True,
                                },
                                {
                                    "name": "owner",
                                    "label": "Owner",
                                    "field": "owner",
                                    "required": True,
                                    "align": "left",
                                    "sortable": True,
                                },
                                {
                                    "name": "creation_date",
                                    "label": "Creation Date",
                                    "field": "creation_date",
                                    "align": "left",
                                    "sortable": True,
                                },
                                {
                                    "name": "actions",
                                    "label": "Actions",
                                    "field": "actions",
                                    "align": "center",
                                    "sortable": False,
                                },
                            ]

                            # Format data for table
                            rows = []
                            for dp in data_products:
                                rows.append(
                                    {
                                        "id": dp.id,
                                        "schema_name": dp.schema_name,
                                        "description": dp.description or "—",
                                        "owner": dp.owner,
                                        "creation_date": dp.creation_date.strftime("%Y-%m-%d %H:%M")
                                        if dp.creation_date
                                        else "—",
                                        "actions": dp.id,
                                    }
                                )

                            table = ui.table(
                                columns=columns,
                                rows=rows,
                                selection=None,
                                pagination={
                                    "sortBy": "creation_date",
                                    "descending": True,
                                    "page": 1,
                                    "rowsPerPage": 10,
                                },
                            ).classes("w-full")

                            # Add action buttons to each row
                            with table.add_slot("body-cell-actions"):
                                ui.html("""
                                <q-td :props="props">
                                    <q-btn flat round color="primary" icon="edit" size="sm" @click="$parent.$emit('edit', props.row)">
                                        <q-tooltip>Edit</q-tooltip>
                                    </q-btn>
                                    <q-btn flat round color="negative" icon="delete" size="sm" @click="$parent.$emit('delete', props.row)" class="ml-1">
                                        <q-tooltip>Delete</q-tooltip>
                                    </q-btn>
                                </q-td>
                                """)

                            # Handle edit and delete events
                            table.on("edit", lambda e: show_edit_dialog(e.args["id"]))
                            table.on("delete", lambda e: show_delete_dialog(e.args["id"], e.args["schema_name"]))

                except Exception as e:
                    logger.error(f"Error refreshing data products table: {e}")
                    ui.notify(f"Error loading data products: {str(e)}", type="negative")

            def show_add_dialog():
                """Show dialog to add a new data product."""
                with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
                    ui.label("Add New Data Product").classes("text-xl font-bold mb-4")

                    schema_name_input = ui.input("Schema Name", placeholder="e.g., sales_analytics")
                    schema_name_input.classes("w-full mb-4").props("outlined")

                    description_input = ui.textarea(
                        "Description", placeholder="Optional description of the data product"
                    )
                    description_input.classes("w-full mb-4").props("outlined rows=3")

                    owner_input = ui.input("Owner", placeholder="e.g., john.doe@company.com")
                    owner_input.classes("w-full mb-4").props("outlined")

                    ui.label("Creation Date").classes("text-sm font-medium text-gray-700 mb-1")
                    creation_date_input = ui.date(value=date.today().isoformat())
                    creation_date_input.classes("w-full mb-4")

                    with ui.row().classes("w-full justify-end gap-2 mt-6"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        save_btn = ui.button("Save", on_click=lambda: save_new_data_product())
                        save_btn.classes("bg-primary text-white")

                def save_new_data_product():
                    """Save the new data product."""
                    try:
                        # Validate inputs
                        if not schema_name_input.value or not schema_name_input.value.strip():
                            ui.notify("Schema name is required", type="negative")
                            return

                        if not owner_input.value or not owner_input.value.strip():
                            ui.notify("Owner is required", type="negative")
                            return

                        # Parse creation date
                        creation_date = None
                        if creation_date_input.value:
                            if isinstance(creation_date_input.value, str):
                                creation_date = datetime.fromisoformat(creation_date_input.value)
                            elif hasattr(creation_date_input.value, "year"):
                                creation_date = datetime.combine(creation_date_input.value, datetime.min.time())

                        # Create data product
                        data_product_data = DataProductCreate(
                            schema_name=schema_name_input.value.strip(),
                            description=description_input.value.strip() if description_input.value else None,
                            owner=owner_input.value.strip(),
                            creation_date=creation_date,
                        )

                        create_data_product(data_product_data)
                        ui.notify(f'Data product "{schema_name_input.value}" created successfully!', type="positive")
                        dialog.close()
                        refresh_table()

                    except ValueError as e:
                        ui.notify(str(e), type="negative")
                    except Exception as e:
                        logger.error(f"Error creating data product: {e}")
                        ui.notify(f"Error creating data product: {str(e)}", type="negative")

                dialog.open()

            def show_edit_dialog(data_product_id: int):
                """Show dialog to edit an existing data product."""
                try:
                    data_product = get_data_product_by_id(data_product_id)
                    if data_product is None:
                        ui.notify("Data product not found", type="negative")
                        return

                    with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
                        ui.label("Edit Data Product").classes("text-xl font-bold mb-4")

                        schema_name_input = ui.input("Schema Name", value=data_product.schema_name)
                        schema_name_input.classes("w-full mb-4").props("outlined")

                        description_input = ui.textarea("Description", value=data_product.description or "")
                        description_input.classes("w-full mb-4").props("outlined rows=3")

                        owner_input = ui.input("Owner", value=data_product.owner)
                        owner_input.classes("w-full mb-4").props("outlined")

                        ui.label("Creation Date").classes("text-sm font-medium text-gray-700 mb-1")
                        creation_date_value = (
                            data_product.creation_date.date() if data_product.creation_date else date.today()
                        )
                        creation_date_input = ui.date(value=creation_date_value.isoformat())
                        creation_date_input.classes("w-full mb-4")

                        with ui.row().classes("w-full justify-end gap-2 mt-6"):
                            ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                            save_btn = ui.button("Save Changes", on_click=lambda: save_data_product_changes())
                            save_btn.classes("bg-primary text-white")

                    def save_data_product_changes():
                        """Save changes to the data product."""
                        try:
                            # Validate inputs
                            if not schema_name_input.value or not schema_name_input.value.strip():
                                ui.notify("Schema name is required", type="negative")
                                return

                            if not owner_input.value or not owner_input.value.strip():
                                ui.notify("Owner is required", type="negative")
                                return

                            # Parse creation date
                            creation_date = None
                            if creation_date_input.value:
                                if isinstance(creation_date_input.value, str):
                                    creation_date = datetime.fromisoformat(creation_date_input.value)
                                elif hasattr(creation_date_input.value, "year"):
                                    creation_date = datetime.combine(creation_date_input.value, datetime.min.time())

                            # Update data product
                            updates = DataProductUpdate(
                                schema_name=schema_name_input.value.strip(),
                                description=description_input.value.strip() if description_input.value else None,
                                owner=owner_input.value.strip(),
                                creation_date=creation_date,
                            )

                            updated_product = update_data_product(data_product_id, updates)
                            if updated_product is None:
                                ui.notify("Failed to update data product", type="negative")
                                return

                            ui.notify(
                                f'Data product "{schema_name_input.value}" updated successfully!', type="positive"
                            )
                            dialog.close()
                            refresh_table()

                        except ValueError as e:
                            ui.notify(str(e), type="negative")
                        except Exception as e:
                            logger.error(f"Error updating data product: {e}")
                            ui.notify(f"Error updating data product: {str(e)}", type="negative")

                    dialog.open()

                except Exception as e:
                    logger.error(f"Error loading data product for edit: {e}")
                    ui.notify(f"Error loading data product: {str(e)}", type="negative")

            def show_delete_dialog(data_product_id: int, schema_name: str):
                """Show confirmation dialog for deleting a data product."""
                with ui.dialog() as dialog, ui.card().classes("w-96 p-6"):
                    ui.label("Confirm Deletion").classes("text-xl font-bold mb-4 text-red-600")
                    ui.label(f'Are you sure you want to delete the data product "{schema_name}"?').classes("mb-4")
                    ui.label("This action cannot be undone.").classes("text-sm text-gray-500 mb-6")

                    with ui.row().classes("w-full justify-end gap-2"):
                        ui.button("Cancel", on_click=lambda: dialog.close()).props("outline")
                        delete_btn = ui.button("Delete", on_click=lambda: confirm_delete())
                        delete_btn.classes("bg-red-500 text-white hover:bg-red-600")

                def confirm_delete():
                    """Confirm and execute the deletion."""
                    try:
                        success = delete_data_product(data_product_id)
                        if success:
                            ui.notify(f'Data product "{schema_name}" deleted successfully!', type="warning")
                            dialog.close()
                            refresh_table()
                        else:
                            ui.notify("Failed to delete data product", type="negative")
                    except Exception as e:
                        logger.error(f"Error deleting data product: {e}")
                        ui.notify(f"Error deleting data product: {str(e)}", type="negative")

                dialog.open()

            # Initial table load
            refresh_table()

    @ui.page("/")
    def index():
        """Redirect home page to data products."""
        ui.navigate.to("/data-products")
