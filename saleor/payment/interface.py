from dataclasses import InitVar, dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from ..order import FulfillmentLineData
from ..order.fetch import OrderLineInfo
from ..payment.models import TransactionEvent, TransactionItem

if TYPE_CHECKING:
    from ..account.models import User
    from ..app.models import App
    from ..channel.models import Channel
    from ..checkout.models import Checkout
    from ..order.models import Order, OrderGrantedRefund

JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
JSONType = Union[Dict[str, JSONValue], List[JSONValue]]


@dataclass
class StoredPaymentMethodRequestDeleteResponseData:
    """Dataclass for storing the response information from payment app."""

    success: bool
    message: Optional[str] = None


@dataclass
class StoredPaymentMethodRequestDeleteData:
    """Dataclass for storing the request information for payment app."""

    payment_method_id: str
    user: "User"
    channel: "Channel"


@dataclass
class PaymentGateway:
    """Dataclass for storing information about a payment gateway."""

    id: str
    name: str
    currencies: List[str]
    config: List[Dict[str, Any]]


@dataclass
class ListStoredPaymentMethodsRequestData:
    channel: "Channel"
    user: "User"


@dataclass
class PaymentMethodCreditCardInfo:
    brand: str
    last_digits: str
    exp_month: int
    exp_year: int
    first_digits: Optional[str] = None


@dataclass
class PaymentMethodData:
    """Payment method data.

    Represents a payment method stored for user (tokenized) in payment gateway, such
    as credit card or SEPA direct debit

    id - ID of stored payment method used to make payment actions
    type - Type of the payment method
    gateway - The app that owns the payment method
    external_id - ID of the payment method in the payment gateway
    supported_payment_flows - List of supported flows that can be performed with this
    payment method
    credit_card_info - Credit card information if the payment method is a credit card
    name -  Name of the payment method. Example: last 4 digits of credit card,
    obfuscated email
    data - JSON data returned by Payment Provider app for this payment method
    """

    id: str
    type: str
    external_id: str
    gateway: PaymentGateway
    supported_payment_flows: List[str] = field(default_factory=list)
    credit_card_info: Optional[PaymentMethodCreditCardInfo] = None
    name: Optional[str] = None
    data: Optional[JSONType] = None


@dataclass
class TransactionActionData:
    action_type: str
    transaction: TransactionItem
    event: "TransactionEvent"
    transaction_app_owner: Optional["App"]
    action_value: Optional[Decimal] = None
    granted_refund: Optional["OrderGrantedRefund"] = None


@dataclass
class TransactionRequestEventResponse:
    psp_reference: Optional[str]
    type: str
    amount: Decimal
    time: Optional[datetime] = None
    external_url: Optional[str] = ""
    message: Optional[str] = ""


@dataclass
class TransactionRequestResponse:
    psp_reference: Optional[str]
    available_actions: Optional[List[str]] = None
    event: Optional["TransactionRequestEventResponse"] = None


@dataclass
class TransactionData:
    token: str
    is_success: bool
    kind: str
    gateway_response: JSONType
    amount: Dict[str, str]


@dataclass
class PaymentGatewayData:
    app_identifier: str
    data: Optional[Dict[Any, Any]] = None
    error: Optional[str] = None


@dataclass
class TransactionProcessActionData:
    action_type: str
    amount: Decimal
    currency: str


@dataclass
class TransactionSessionData:
    transaction: "TransactionItem"
    source_object: Union["Checkout", "Order"]
    action: TransactionProcessActionData
    payment_gateway_data: PaymentGatewayData


@dataclass
class TransactionSessionResult:
    app_identifier: str
    response: Optional[Dict[Any, Any]] = None
    error: Optional[str] = None


@dataclass
class PaymentMethodInfo:
    """Uniform way to represent payment method information."""

    first_4: Optional[str] = None
    last_4: Optional[str] = None
    exp_year: Optional[int] = None
    exp_month: Optional[int] = None
    brand: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None


@dataclass
class GatewayResponse:
    """Dataclass for storing gateway response.

    Used for unifying the representation of gateway response.
    It is required to communicate between Saleor and given payment gateway.
    """

    is_success: bool
    action_required: bool
    kind: str  # use "TransactionKind" class
    amount: Decimal
    currency: str
    transaction_id: str
    error: Optional[str]
    customer_id: Optional[str] = None
    payment_method_info: Optional[PaymentMethodInfo] = None
    raw_response: Optional[Dict[str, str]] = None
    action_required_data: Optional[JSONType] = None
    # Some gateway can process transaction asynchronously. This value define if we
    # should create new transaction based on this response
    transaction_already_processed: bool = False
    psp_reference: Optional[str] = None


@dataclass
class AddressData:
    first_name: str
    last_name: str
    company_name: str
    street_address_1: str
    street_address_2: str
    city: str
    city_area: str
    postal_code: str
    country: str
    country_area: str
    phone: str
    metadata: Optional[dict]
    private_metadata: Optional[dict]


class StorePaymentMethodEnum(str, Enum):
    NONE = "NONE"
    ON_SESSION = "ON_SESSION"
    OFF_SESSION = "OFF_SESSION"


@dataclass
class PaymentLineData:
    amount: Decimal
    variant_id: int
    product_name: str
    product_sku: Optional[str]
    quantity: int


@dataclass
class PaymentLinesData:
    shipping_amount: Decimal
    voucher_amount: Decimal
    lines: List[PaymentLineData]


@dataclass
class RefundData:
    order_lines_to_refund: List[OrderLineInfo] = field(default_factory=list)
    fulfillment_lines_to_refund: List[FulfillmentLineData] = field(default_factory=list)
    refund_shipping_costs: bool = False
    refund_amount_is_automatically_calculated: bool = True


@dataclass
class PaymentData:
    """Dataclass for storing all payment information.

    Used for unifying the representation of data.
    It is required to communicate between Saleor and given payment gateway.
    """

    gateway: str
    amount: Decimal
    currency: str
    billing: Optional[AddressData]
    shipping: Optional[AddressData]
    payment_id: int
    graphql_payment_id: str
    order_id: Optional[str]
    customer_ip_address: Optional[str]
    customer_email: str
    order_channel_slug: Optional[str] = None
    token: Optional[str] = None
    customer_id: Optional[str] = None  # stores payment gateway customer ID
    reuse_source: bool = False  # Note: this field will be removed in 4.0.
    data: Optional[dict] = None
    graphql_customer_id: Optional[str] = None
    checkout_token: Optional[str] = None
    checkout_metadata: Optional[Dict] = None
    store_payment_method: StorePaymentMethodEnum = StorePaymentMethodEnum.NONE
    payment_metadata: Dict[str, str] = field(default_factory=dict)
    psp_reference: Optional[str] = None
    refund_data: Optional[RefundData] = None
    transactions: List[TransactionData] = field(default_factory=list)
    # Optional, lazy-evaluated gateway arguments
    _resolve_lines_data: InitVar[Callable[[], PaymentLinesData]] = None

    def __post_init__(self, _resolve_lines_data: Callable[[], PaymentLinesData]):
        self.__resolve_lines_data = _resolve_lines_data

    # Note: this field does not appear in webhook payloads,
    # because it's not visible to dataclasses.asdict
    @cached_property
    def lines_data(self) -> PaymentLinesData:
        return self.__resolve_lines_data()


@dataclass
class TokenConfig:
    """Dataclass for payment gateway token fetching customization."""

    customer_id: Optional[str] = None


@dataclass
class GatewayConfig:
    """Dataclass for storing gateway config data.

    Used for unifying the representation of config data.
    It is required to communicate between Saleor and given payment gateway.
    """

    gateway_name: str
    auto_capture: bool
    supported_currencies: str
    # Each gateway has different connection data so we are not able to create
    # a unified structure
    connection_params: Dict[str, Any]
    store_customer: bool = False
    require_3d_secure: bool = False


@dataclass
class CustomerSource:
    """Dataclass for storing information about stored payment sources in gateways."""

    id: str
    gateway: str
    credit_card_info: Optional[PaymentMethodInfo] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class InitializedPaymentResponse:
    gateway: str
    name: str
    data: Optional[JSONType] = None
