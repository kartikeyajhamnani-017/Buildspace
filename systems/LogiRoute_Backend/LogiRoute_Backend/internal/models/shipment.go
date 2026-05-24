package models 
 
import(
	"time"
	"go.mongodb.org/mongo-driver/v2/bson"

)

type ShipmentStatus string

const (
	StatusCreated  ShipmentStatus = "created"
	StatusAssigned ShipmentStatus = "assigned"
	StatusInTransit ShipmentStatus = "in_transit"
	StatusDelivered ShipmentStatus = "delivered"
)

type PackageDimensions struct {
	Length float64 `bson:"length" json:"length"`
	Width  float64 `bson:"width" json:"width"`
	Height float64 `bson:"height" json:"height"`

}
type Package struct {
	Description string `bson:"description" json:"description"`
	Weight float64 `bson:"weight" json:"weight"`
	Dimensions PackageDimensions `bson:"dimensions" json:"dimensions"`
}

type Shipment struct {
	ID                  bson.ObjectID `bson:"_id,omitempty" json:"id"`
	TrackingNumber      string `bson:"tracking_number" json:"tracking_number"`
	Status              ShipmentStatus `bson:"status" json:"status"`
	PackageDetails      Package `bson:"package_details" json:"package_details"`

	Pickup              Address `bson:"pickup_address" json:"pickup_address"`
	Destination         Address `bson:"destination_address" json:"destination_address"`

	DispatcherID        bson.ObjectID `bson:"dispatcher_id" json:"dispatcher_id"`
	DriverID            *bson.ObjectID `bson:"driver_id" json:"driver_id,omitempty"`

	CreatedAt           time.Time `bson:"created_at" json:"created_at"`
	UpdatedAt           time.Time `bson:"updated_at" json:"updated_at"`
}